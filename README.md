## Twitch fragments uploader

[![](https://images.microbadger.com/badges/image/dimorinny/twitch-fragment-uploader.svg)](https://microbadger.com/images/dimorinny/twitch-fragment-uploader "Get your own image badge on microbadger.com")

Web server for uploading Twitch fragments to [streamable](https://streamable.com/) service, that can used as microservice in your applications. For load stream fragments [livestreamer](https://github.com/chrippa/livestreamer) library is used.

### Run server

```
docker run \
  -p 8080:8080 \
  -e "TWITCH_OAUTH=<TWITCH_OAUTH_TOKEN>" \
  -e "TWITCH_CHANNEL=<CHANNEL_NAME>" \
  dimorinny/twitch-fragment-uploader
```

**Environment parameters:**

* **TWITCH\_OAUTH** - OAuth Twitch token
* **TWITCH\_CHANNEL** - Channel name
* **RING\_BUFFER\_SIZE** - Stream buffer size. This is internal param of [livestreamer](https://github.com/chrippa/livestreamer) library. This parameter determines uploaded fragment size. (20 MB by default)
* **PORT** - Http proxy port (8080 by default)

### Usage

For uploading stream fragment you should execute `GET` request like this:

```
http://127.0.0.1:8080/api/v1/upload
```

After that server returns uploading with video link and name. For example after success request you got response like this:

```
{
  "status": "success",
  "response": {
    "url": "https://streamable.com/e6h19",
    "name": "05.03.17 22:29 cahchec"
  }
}
```

When some error occured during recognition process you got reponse like this:

```
{
  "status": "error",
  "response": {
    "message": "Stream buffer is empty",
    "code": 100
  },
}
```

For more details you should look at stderr.