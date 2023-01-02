<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('images', function (Blueprint $table) {
            $table->id();

            $table->text("file_name");
            $table->text("post_title");
            $table->text("url");
            $table->text("reddit_id");
            $table->integer("upvotes");
            
            $table->text("twitter_media_id")->nullable();
            $table->boolean("downloaded")->default(0);
            $table->boolean("posted")->default(0);
            
            $table->softDeletes();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('images');
    }
};
