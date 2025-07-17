==========
Hollowfire
==========

*The spiritual successor to Rubicon.*

----

What is Hollowfire/Hollowserver?
================================

Hollowfire is a locally hosted AI provider/server, primarily focusing on the primary personality, being... Well... Hollowfire.
Unlike its predecessor projects, it was designed with plug and play in mind from the very beginning, from its structure, to how it operates on a basic level.
Just make a HTTP request or two, and you're good to go! One instance of Hollowserver can handle everything - Different providers, different models, separating conversations,
and so on, so forth.

It *is* admittedly a little unnecessary, it does have it's limitations, and it fills a very specific niche with interest from a select few...
But personally, it's extremely convenient for me, and I'm sure it'll be convenient for said select few.

What are some things it's planned to be able to do/already does?
----------------------------------------------------------------

Also could be treated as an extension of the prior section...

As said earlier in the 'What is Hollowfire/Hollowserver?' section, it's an entire HTTP server interacting with the basic AI. It has support for different APIs,
including locally ran ones.

Hollowfire is the spiritual successor to Rubicon.
Rubicon was a large, bulky, and complicated monolithic mess.
The earlier versions had no form of plug-and-play at all, instead being entirely tethered to whatever application it was integrated into,
with later versions being nearly just as bad with attempts at a live-patching form of plug-and-play, which was a horrible idea from the beginning, still keeping it
tethered to the application.

Hollowfire is the result of learning from all of these mistakes, thus becoming only a provider for the interfaces for those apps.

Now, to the actual point - This allows it to do many, many things. As long as the core is running, every app can share a conversation memory,
the interfaces can be started, and stopped, and restarted, and hot-reloaded, modified, and it no longer takes the AI with it, because the core is separate.

You could do so many things with Hollowserver, without needing to put much work into it.
You could add it into a game, you could even add it into your desktop environment using whatever flavor of addon it provides.

Why an HTTP server and not just an importable library? I don't fancy having to copy a file each time, especially when that file has multiple other source files attached
and just simply isn't portable to begin with.

*As of writing, the API is still a work in progress.*

----

Some other things I'd like to do...

* Long-term Memory (LTS)
* Default/Built-in tools
* ...


How do I set it up?
===================
There's hardly any setup required.
The command line arguments have help text to guide you, but really, it's mostly running the ?/main.py file.

How can I contribute?
=====================
Like you would any other Git project, really.
Fork it, make your changes, and submit a pull request or your proposed patches.

License
=======
I believe in open, free, and fair software for all.
Hollowfire is licensed under the GNU General Public License v3. See the LICENSE file for more information.

EXTRAS
------
For those who have been following along with Hollowfire's development, yet come to this repository on it's first few commits and see it empty...
This is Hollowfire 1.0, or, planned to be. There was, and is, a fully functional prototype server, but this repository and that prototype are *separate!*
You most likely saw the prototype in action, but this is the real deal.
