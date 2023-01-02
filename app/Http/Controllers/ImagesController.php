<?php

namespace App\Http\Controllers;

use Inertia\Inertia;
use App\Models\Image;
use Illuminate\Support\Facades\Schema;

class ImagesController extends Controller
{
    /**
     * Display the Images page
     * 
     * @return \Inertia\Response
     */
    public function index() {
        return Inertia::render("Images", [
            "rows" => Image::all(),
            "header" => Schema::getColumnListing('images'),
        ]);
    }
}
