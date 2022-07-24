# asyncbbb - async BigBlueButton API Client for Python
<p>
    <a href="https://pypi.org/project/asyncbbb" target="_blank">
        <img src="https://img.shields.io/pypi/v/asyncbbb?color=%2334D058&label=pypi%20package" alt="Package version">
    </a>
    <a href="https://pypi.org/project/asyncbbb" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/asyncbbb.svg?color=%2334D058" alt="Supported Python versions" />
    </a>
    <a href="https://github.com/SebastianLuebke/asyncbbb/blob/main/LICENSE" target="_blank">
        <img src="https://img.shields.io/github/license/sebastianluebke/asyncbbb?color=%2334D058" />
    </a>
</p>

## Installation
```
pip install asyncbbb
```

## Usage
```python
import asyncio

from asyncbbb import BigBlueButton

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