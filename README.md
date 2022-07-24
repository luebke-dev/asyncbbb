# asyncbbb - async BigBlueButton API Client for Python


## Installation
```
pip install asyncbbb
```

## Usage
```python
import asyncio


async def test():
    bbb = BigBlueButton(
        "https://<HOSTNAME>/bigbluebutton", "<SHARED_SECRET>"
    )


    try:
        response = await bbb.create(name="Test Meeting", meeting_id="TestMeeting", allow_requests_without_session=True)
    except BigBlueButtonException as e:
        if e.message_key == "idNotUnique":
            pass

    data = await bbb.join(full_name="Sebastian Lübke", meeting_id="TestMeeting", redirect=False, role="MODERATOR")
    print(data)

asyncio.run(test())

```

## TODO
Write tests