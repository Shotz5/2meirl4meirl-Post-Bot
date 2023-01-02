<?php

namespace App\Http\Controllers;

use App\Models\Image;
use Illuminate\Support\Facades\Storage;
use Abraham\TwitterOAuth\TwitterOAuth;

class TwitterController extends Controller
{
    /**
     * Post an image to Twitter
     * 
     * @return bool
     */
    public static function post() {
        $image = Image::where("downloaded", 0, "and")
                ->where("posted", 0)
                ->orderBy("upvotes", "desc")
                ->first();
        $auth = new TwitterOAuth(env("CONSUMER_KEY"), env("CONSUMER_SECRET"), env("ACCESS_TOKEN"), env("ACCESS_TOKEN_SECRET"));

        $content = $auth->get("account/verify_credentials");

        if ($auth->getLastHttpCode() != 200) {
            throw new \Error("Failed to verify credentials");
        }

        if (!self::uploadPhoto($image, $auth)) {
            throw new \Error("Failed to upload photo to Twitter");
        }

        if (!self::tweetPhoto($image, $auth)) {
            throw new \Error("Failed to tweet photo to Twitter");
        }

        return true;
    }

    /**
     * Upload an image to Twitter
     * 
     * @return array|bool
     */
    private static function uploadPhoto(Image $image, TwitterOAuth $auth) {
        // Download image
        Storage::disk("images")->put($image->file_name, file_get_contents($image->url));

        // Update image results in db
        $image->downloaded = 1;

        // Upload image to Twitter
        $media_info = $auth->upload(
            "media/upload",
            ['media' => Storage::disk("images")->path($image->file_name)]
        );

        if ($auth->getLastHttpCode() == 200) {
            $image->twitter_media_id = $media_info->media_id_string;
            $image->save();
            return true;
        } else {
            return false;
        }
    }

    private static function tweetPhoto(Image $image, TwitterOAuth $auth) {
        $result = $auth->post('statuses/update', [
            'text' => $image->post_title . " redd.it/" . $image->reddit_id,
            'media_ids' => [$image->twitter_media_id]
        ]);

        if ($auth->getLastHttpCode() == 200) {
            $image->posted = 1;
            $image->save();
            return true;
        } else {
            return false;
        }
    }
}
