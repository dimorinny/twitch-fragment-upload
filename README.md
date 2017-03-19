## Twitch fragments uploader

[![](https://images.microbadger.com/badges/image/dimorinny/twitch-fragment-uploader.svg)](https://microbadger.com/images/dimorinny/twitch-fragment-uploader "Get your own image badge on microbadger.com")

Web server for uploading Twitch fragments to [vk](https://vk.com/)   group service, that can used as microservice in your applications. For load stream fragments [livestreamer](https://github.com/chrippa/livestreamer) library is used.

### Run server

```
docker run \
  -p 8080:8080 \
  -e "TWITCH_OAUTH=<TWITCH_OAUTH_TOKEN>" \
  -e "TWITCH_CHANNEL=<CHANNEL_NAME>" \
  -e "VK_OAUTH=<VK_OAUTH_TOKEN>" \
  -e "VK_GROUP_ID=<VK_GROUP_ID>" \
  -e "TIMEZONE=<TIMEZONE>" \
dimorinny/twitch-fragment-uploader
```

**Environment parameters:**

* **TWITCH\_OAUTH** - OAuth Twitch token
* **TWITCH\_CHANNEL** - Twitch channel name
* **VK\_OAUTH** - OAuth Vk token.
* **VK\_GROUP** - Vk group id (without `-`), where video will be uploaded
* **TIMEZONE** - Uploaded video name generates from current date using passed timezone. For understand timezone format you can look at [specification](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
* **RING\_BUFFER\_SIZE** - Stream buffer size. This is internal param of [livestreamer](https://github.com/chrippa/livestreamer) library. This parameter determines uploaded fragment size. (10 MB by default)
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
    "url": "https://vk.com/video_ext.php?oid=-142832429&id=456233077&hash=3d84b9ccf4e94405",
    "name": "05.03.17 22:29 cahchec"
  }
}
```

When some error occurred during recognition process you got reponse like this:

```
{
  "status": "error",
  "response": {
    "message": "Stream buffer is empty",
    "code": 100
  }
}
```

For more details you should look at stderr.