<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Http;
use App\Models\Image;

class RedditController extends Controller
{
    /**
     * Fetch hot posts from Reddit
     * 
     * @return bool
     */
    public static function fetch() {
        $response = Http::get("https://reddit.com/r/2meirl4meirl/hot/.json");

        if ($response->status() == 200) {
            $json = $response->json();
            foreach ($json["data"]["children"] as $entry) {
                if (array_key_exists("preview", $entry["data"]) && !$entry["data"]["is_video"]) {
                    $split = explode("/", $entry["data"]["url"]);
                    $last = $split[array_key_last($split)];
                    $image = new Image([
                        'file_name' => $last,
                        'url' => $entry["data"]["url"],
                        'post_title' => $entry["data"]["title"],
                        'reddit_id' => $entry["data"]["id"],
                        'upvotes' => $entry["data"]["ups"],
                        'downloaded' => 0,
                        'posted' => 0,
                    ]);
                    $image->save();
                }
            }
            return true;
        } else {
            return false;
        }
    }
}
