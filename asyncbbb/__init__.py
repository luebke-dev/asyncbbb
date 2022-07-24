import hashlib
import os
import urllib.parse
from typing import Any, Dict, List, Optional, Union

import aiofiles
import httpx
import xml2dict


class BigBlueButtonException(Exception):
    def __init__(self, message_key, message):
        self.message_key = message_key
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message_key} -> {self.message}"


class BigBlueButton:
    def __init__(self, api_url: str, shared_secret: str):
        self.client = httpx.AsyncClient()
        self.api_url = api_url
        self.shared_secret = shared_secret

    def _process_value(self, key, value):
        if type(value) == bool:
            if value:
                value = "true"
            else:
                value = "false"
        elif type(value) == list:
            value = ",".join(value)
        elif key == "meta" and type(value) == dict:
            meta = []
            for k, v in value.items():
                meta.append(self._process_value("meta_" + k, v))
            return meta
        result = f"{key}={urllib.parse.quote(value)}"
        return result

    def _build_query_string(self, endpoint: str, data: Dict[Any, Any]):
        params = []
        for key, value in data.items():
            if value is None:
                continue
            value = self._process_value(key, value)
            if type(value) == list:
                params.extend(value)
            else:
                params.append(value)

        build_checksum_str = f"{endpoint}{'&'.join(params)}{self.shared_secret}"

        hash = hashlib.sha1(build_checksum_str.encode("utf-8"))
        checksum = hash.hexdigest()
        params.append(f"checksum={checksum}")

        return f"?{'&'.join(params)}"

    async def _make_request(
        self,
        *,
        method: str = "GET",
        endpoint: str,
        data: Optional[Dict[Any, Any]] = {},
        file: Optional[Dict[Any, Any]] = None,
        json_response: bool = False,
    ) -> Dict[Any, Any]:
        params = self._build_query_string(endpoint, data)
        response = await self.client.request(
            method, f"{self.api_url}/api/{endpoint}{params}", files=file
        )

        if response.status_code != 200:
            raise BigBlueButtonException(response.status_code, "")

        try:
            if json_response:
                parsed_response = response.json()
            else:
                parsed_response = xml2dict.parse(response.text)
        except Exception as e:
            raise BigBlueButtonException("parsingError", str(e))

        parsed_response = parsed_response["response"]
        if parsed_response["returncode"] != "SUCCESS":
            raise BigBlueButtonException(
                parsed_response["messageKey"], parsed_response["message"]
            )

        return parsed_response

    async def get_api_version(self):
        response = await self._make_request(endpoint="")
        return response

    async def create(
        self,
        name: str,
        meeting_id: str,
        attendee_pw: Optional[str] = None,
        moderator_pw: Optional[str] = None,
        welcome: Optional[str] = None,
        dial_number: Optional[str] = None,
        voice_bridge: Optional[str] = None,
        max_participants: Optional[int] = None,
        logout_url: Optional[str] = None,
        record: Optional[bool] = None,
        duration: Optional[int] = None,
        is_breakout: Optional[bool] = None,
        parent_meeting_id: Optional[str] = None,
        sequence: Optional[int] = None,
        free_join: Optional[bool] = None,
        breakout_rooms_enabled: Optional[bool] = None,
        breakout_rooms_private_chat_enabled: Optional[bool] = None,
        breakout_rooms_record: Optional[bool] = None,
        meta: Optional[Dict[str, str]] = None,
        moderator_only_message: Optional[str] = None,
        auto_start_recording: Optional[bool] = None,
        allow_start_stop_recording: Optional[bool] = None,
        webcams_only_for_moderator: Optional[bool] = None,
        banner_text: Optional[str] = None,
        banner_color: Optional[str] = None,
        mute_on_start: Optional[bool] = None,
        allow_mods_to_unmute_users: Optional[bool] = None,
        lock_settings_disable_cam: Optional[bool] = None,
        lock_settings_disable_mic: Optional[bool] = None,
        lock_settings_disable_private_chat: Optional[bool] = None,
        lock_settings_disable_public_chat: Optional[bool] = None,
        lock_settings_disable_note: Optional[bool] = None,
        lock_settings_locked_layout: Optional[bool] = None,
        lock_settings_lock_on_join: Optional[bool] = None,
        lock_settings_lock_on_join_configurable: Optional[bool] = None,
        lock_settings_hide_viewer_cursor: Optional[bool] = None,
        guest_policy: Optional[str] = None,
        meeting_keep_events: Optional[bool] = None,
        end_when_no_moderator: Optional[bool] = None,
        end_when_no_moderator_delay_in_minutes: Optional[int] = None,
        meeting_layout: Optional[str] = None,
        learning_dashboard_enabled: Optional[bool] = None,
        learning_dashboard_cleanup_delay_in_minutes: Optional[int] = None,
        allow_mods_to_eject_cameras: Optional[bool] = None,
        allow_requests_without_session: Optional[bool] = None,
        virtual_background_disabled: Optional[bool] = None,
        user_camera_cap: Optional[int] = None,
        meeting_camera_cap: Optional[int] = None,
        groups: Optional[List[Dict[str, str]]] = None,
        logo: Optional[str] = None,
        disabled_features: Optional[List[str]] = None,
        pre_uploaded_presentation_override_default: Optional[bool] = None,
    ):
        response = await self._make_request(
            endpoint="create",
            data={
                "name": name,
                "meetingID": meeting_id,
                "attendeePW": attendee_pw,
                "moderatorPW": moderator_pw,
                "welcome": welcome,
                "dialNumber": dial_number,
                "voiceBridge": voice_bridge,
                "maxParticipants": max_participants,
                "logoutURL": logout_url,
                "record": record,
                "duration": duration,
                "isBreakout": is_breakout,
                "parentMeetingID": parent_meeting_id,
                "sequence": sequence,
                "freeJoin": free_join,
                "breakoutRoomsEnabled": breakout_rooms_enabled,
                "breakoutRoomsPrivateChatEnabled": breakout_rooms_private_chat_enabled,
                "breakoutRoomsRecord": breakout_rooms_record,
                "meta": meta,
                "moderatorOnlyMessage": moderator_only_message,
                "autoStartRecording": auto_start_recording,
                "allowStartStopRecording": allow_start_stop_recording,
                "webcamsOnlyForModerator": webcams_only_for_moderator,
                "bannerText": banner_text,
                "bannerColor": banner_color,
                "muteOnStart": mute_on_start,
                "allowModsToUnmuteUsers": allow_mods_to_unmute_users,
                "lockSettingsDisableCam": lock_settings_disable_cam,
                "lockSettingsDisableMic": lock_settings_disable_mic,
                "lockSettingsDisablePrivateChat": lock_settings_disable_private_chat,
                "lockSettingsDisablePublicChat": lock_settings_disable_public_chat,
                "lockSettingsDisableNote": lock_settings_disable_note,
                "lockSettingsLockedLayout": lock_settings_locked_layout,
                "lockSettingsLockOnJoin": lock_settings_lock_on_join,
                "lockSettingsLockOnJoinConfigurable": lock_settings_lock_on_join_configurable,
                "lockSettingsHideViewerCursor": lock_settings_hide_viewer_cursor,
                "guestPolicy": guest_policy,
                "meetingKeepEvents": meeting_keep_events,
                "endWhenNoModerator": end_when_no_moderator,
                "endWhenNoModeratorDelayInMinutes": end_when_no_moderator_delay_in_minutes,
                "meetingLayout": meeting_layout,
                "learningDashBoardEnabled": learning_dashboard_enabled,
                "learningDashboardCleanupDelayInMinutes": learning_dashboard_cleanup_delay_in_minutes,
                "allowModsToEjectCameras": allow_mods_to_eject_cameras,
                "allowRequestsWithoutSession": allow_requests_without_session,
                "virtualBackgroundDisabled": virtual_background_disabled,
                "userCameraCap": user_camera_cap,
                "meetingCameraCap": meeting_camera_cap,
                "groups": groups,
                "logo": logo,
                "disabledFeatures": disabled_features,
                "preUploadedPresentationOverrideDefault": pre_uploaded_presentation_override_default,
            },
        )
        return response

    async def join(
        self,
        *,
        full_name: str,
        meeting_id: str,
        password: Optional[str] = None,
        role: str,
        create_time: Optional[str] = None,
        user_id: Optional[str] = None,
        web_voice_conf: Optional[str] = None,
        config_token: Optional[str] = None,
        default_layout: Optional[str] = None,
        avatar_url: Optional[str] = None,
        redirect: Optional[bool] = None,
        client_url: Optional[str] = None,
        guest: Optional[str] = None,
        excluded_from_dashboard: Optional[str] = None,
    ):
        response = await self._make_request(
            endpoint="join",
            data={
                "fullName": full_name,
                "meetingID": meeting_id,
                "password": password,
                "role": role,
                "createTime": create_time,
                "userID": user_id,
                "webVoiceConf": web_voice_conf,
                "configToken": config_token,
                "defaultLayout": default_layout,
                "avatarUrl": avatar_url,
                "redirect": redirect,
                "clientUrl": client_url,
                "guest": guest,
                "excludedFromDashboard": excluded_from_dashboard,
            },
        )
        return response

    async def end(
        self,
        *,
        meeting_id: str,
    ):
        response = await self._make_request(
            endpoint="end",
            data={
                "meetingID": meeting_id,
            },
        )
        return response

    async def insert_document(self):
        raise BigBlueButtonException(
            "notYetImplemented", "This request is not yet implemented"
        )

    async def is_meeting_running(
        self,
        *,
        meeting_id: str,
    ):
        response = await self._make_request(
            endpoint="isMeetingRunning",
            data={
                "meetingID": meeting_id,
            },
        )
        return response

    async def get_meetings(self):
        response = await self._make_request(endpoint="getMeetings")
        return response

    async def get_meeting_info(
        self,
        *,
        meeting_id: str,
    ):
        response = await self._make_request(
            endpoint="getMeetingInfo",
            data={
                "meetingID": meeting_id,
            },
        )
        return response

    async def get_recordings(
        self,
        *,
        meeting_id: Optional[str] = None,
        record_id: Optional[Union[str, List[str]]] = None,
        state: Optional[str] = None,
        meta: Optional[Dict[str, str]] = None,
    ):
        response = await self._make_request(
            endpoint="getRecordings",
            data={
                "meetingID": meeting_id,
                "recordID": record_id,
                "state": state,
                "meta": meta,
            },
        )
        data = [recording for key, recording in response["recordings"].items()]

        return data

    async def publish_recordings(self, *, record_id: str, publish: bool):
        response = await self._make_request(
            endpoint="getRecordings", data={"recordID": record_id, "publish": publish}
        )
        return response

    async def delete_recordings(self, *, record_id: Union[str, List[str]]):
        response = await self._make_request(
            endpoint="deleteRecordings",
            data={
                "recordID": record_id,
            },
        )
        return response

    async def update_recordings(
        self, *, record_id: Union[str, List[str]], meta: Dict[str, str]
    ):
        response = await self._make_request(
            endpoint="updateRecordings", data={"recordID": record_id, "meta": meta}
        )
        return response

    async def get_recording_text_tracks(self, record_id: str):
        response = await self._make_request(
            endpoint="getRecordingTextTracks",
            data={
                "recordID": record_id,
            },
            json_response=True,
        )
        return response["tracks"]

    async def put_recording_text_track(
        self, record_id: str, kind: str, lang: str, label: str, file: str
    ):
        if not os.path.exists(file):
            raise BigBlueButtonException(
                "fileDoesNotExist", "The Upload File does not exists"
            )

        async with aiofiles.open(file, "rb") as file:
            subtitle = await file.read()

        file = {"file": subtitle}
        response = await self._make_request(
            method="POST",
            endpoint="putRecordingTextTrack",
            data={"recordID": record_id, "kind": kind, "lang": lang, "label": label},
            file=file,
            json_response=True,
        )
        return response
