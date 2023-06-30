
.. _supported_file_types:

Supported file types
====================
Telegram-upload supports uploading of any file type supported by Telegram. This includes all common image formats,
video, audio, and document files. But some file types supports extra features like video streaming or audio playback.

This document describes the supported file types and their features. The files are downloaded from
`filesamples.com <https://filesamples.com/>`_ using the ``supported_file_types.py`` script in the ``docs`` folder.

Keep in mind that the results may differ across platforms and Telegram clients. You can contribute by making a `pull
request to the repository <https://github.com/Nekmo/telegram-upload/pulls>`_.

Video file types
----------------
The following section shows the supported video file types and their features. This features includes:

* **Metadata:** The file metadata is extracted correctly using `Hachoir <https://hachoir.readthedocs.io/en/latest/>`_.
* **Video playback:** The video can be played in Telegram.
* **Video streaming:** The video can be streamed while it is being downloaded.

The default file name is *"sample_960x400_ocean_with_audio"* with 960x400 resolution and audio.

3gp
~~~
Third Generation Partnership Project.

* **Metadata:** Yes.
* **Video playback:** No.
* **Video streaming:** No.

asf
~~~
Advanced Systems Format.

* **Metadata:** Yes.
* **Video playback:** No.
* **Video streaming:** No.

avi
~~~
Audio Video Interleave.

* **Metadata:** Yes.
* **Video playback:** No.
* **Video streaming:** No.

f4v
~~~
Flash Video.

* **Metadata:** Yes.
* **Video playback:** No.
* **Video streaming:** No.

flv
~~~
Flash Video.

* **Metadata:** Yes.
* **Video playback:** No.
* **Video streaming:** No.

hevc
~~~~
High Efficiency Video Coding.

* **Metadata:** No.
* **Video playback:** No.
* **Video streaming:** No.

m2ts
~~~~
MPEG-2 Transport Stream.

* **Metadata:** No.
* **Video playback:** No.
* **Video streaming:** No.

m2v
~~~
MPEG-2 Video.

* **Metadata:** No.
* **Video playback:** No.
* **Video streaming:** No.

m4v
~~~
MPEG-4 Video.

* **Metadata:** Yes.
* **Video playback:** Yes.
* **Video streaming:** Yes.

mkv
~~~
Matroska Multimedia Container.

* **Metadata:** Yes.
* **Video playback:** Yes.
* **Video streaming:** No.

mov
~~~
QuickTime File Format.

* **Metadata:** Yes.
* **Video playback:** Yes.
* **Video streaming:** Yes.

mp4
~~~
MPEG-4 Part 14.

* **Metadata:** Yes.
* **Video playback:** Yes.
* **Video streaming:** Yes.

mjpeg
~~~~~
Motion JPEG.

Error uploading the file. See the `issue #204 <https://github.com/Nekmo/telegram-upload/issues/204>`_

mpeg
~~~~
MPEG-1 Video.

* **Metadata:** No.
* **Video playback:** No.
* **Video streaming:** No.

mpg
~~~
MPEG-1 Video.

* **Metadata:** No.
* **Video playback:** No.
* **Video streaming:** No.

mts
~~~
MPEG-2 Transport Stream.

* **Metadata:** No.
* **Video playback:** No.
* **Video streaming:** No.

mxf
~~~
Material Exchange Format.

* **Metadata:** No.
* **Video playback:** No.
* **Video streaming:** No.

ogv
~~~
Ogg Video.

* **Metadata:** Yes.
* **Video playback:** No.
* **Video streaming:** No.

rm
~~
RealMedia.

* **Metadata:** Yes (but width & height are not available).
* **Video playback:** No.
* **Video streaming:** No.

ts
~~
MPEG-2 Transport Stream.

* **Metadata:** No.
* **Video playback:** No.
* **Video streaming:** No.

vob
~~~
DVD Video Object.

* **Metadata:** No.
* **Video playback:** No.
* **Video streaming:** No.

webm
~~~~
WEB Media.

* **Metadata:** Yes.
* **Video playback:** Yes.
* **Video streaming:** No.

wmv
~~~
Windows Media Video.

* **Metadata:** Yes.
* **Video playback:** No.
* **Video streaming:** No.

wtv
~~~
Windows Media Center TV.

* **Metadata:** No.
* **Video playback:** No.
* **Video streaming:** No.

Audio file types
----------------
The following section shows the supported audio file types and their features. This features includes:

* **Metadata:** The file metadata is extracted correctly using `Hachoir <https://hachoir.readthedocs.io/en/latest/>`_.
* **Detected as audio:** The file is detected as audio by Telegram.
* **Audio playback in Telegram desktop:** The audio can be played in Telegram desktop.
* **Audio playback in Telegram Android:** The audio can be played in Telegram android.

The tested Telegram desktop version is *4.8.3* under *GNU/Linux* and the tested Telegram android version is *9.6.7*
under *Android 13* (Google Pixel 6a).

The default file name is *"sample4"* with *4 minutes and 4 seconds* of duration.

8svx
~~~~
8-Bit Sampled Voice.

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

acc
~~~
Advanced Audio Coding.

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

ac3
~~~
Audio Codec 3.

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

aiff
~~~~
Audio Interchange File Format.

* **Metadata:** Yes.
* **Detected as audio:** Yes.
* **Audio playback in Telegram desktop:** Yes.
* **Audio playback in Telegram Android:** No.

amb
~~~
Ambisonic B-Format.

* **Metadata:** Yes.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

au
~~
Sun Microsystems AUdio.

* **Metadata:** Yes.
* **Detected as audio:** Yes.
* **Audio playback in Telegram desktop:** Yes.
* **Audio playback in Telegram Android:** No.

avr
~~~
Audio Visual Research.

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

caf
~~~
Apple Core Audio File.

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

cdda
~~~~
GSM 06.10 Lossy Speech Compression

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

cvs
~~~
Continuously Variable Slope Delta modulation.

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

cvsd
~~~~
Continuously Variable Slope Delta modulation.

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

cvu
~~~
Continuously Variable Slope Delta modulation.

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

dts
~~~
Digital Surround Audio

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

dvms
~~~~
Variable Slope Delta Modulation Audio

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

fap
~~~
PARIS Audio File Format

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

flac
~~~~
Free Lossless Audio Codec

* **Metadata:** Yes.
* **Detected as audio:** Yes.
* **Audio playback in Telegram desktop:** Yes.
* **Audio playback in Telegram Android:** Yes.

fssd
~~~~
FSSD Sound

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

gsrt
~~~~
Grandstream Ring-tone Files

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

hcom
~~~~
Macintosh HCOM files

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

htk
~~~
HTK

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

ima
~~~
Disk Image

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

ircam
~~~~~
Ircam Audio File

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

m4a
~~~
MPEG-4 Apple Lossless Audio Codec

* **Metadata:** Yes.
* **Detected as audio:** Yes (in desktop).
* **Audio playback in Telegram desktop:** Yes.
* **Audio playback in Telegram Android:** No.

m4r
~~~
iTunes Ringtone File

* **Metadata:** Yes.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

maud
~~~~
Amiga MAUD Audio Format

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

mp2
~~~
MPEG-1/2 Audio Layer 2 Format

* **Metadata:** Yes.
* **Detected as audio:** Yes.
* **Audio playback in Telegram desktop:** Yes.
* **Audio playback in Telegram Android:** Partially (no audio) but the progress bar works.

mp3
~~~
MPEG-1 Audio Layer-3

* **Metadata:** Yes.
* **Detected as audio:** Yes.
* **Audio playback in Telegram desktop:** Yes.
* **Audio playback in Telegram Android:** Yes.

nist
~~~~
NIST (National Institute of Standards and Technology)

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

oga
~~~
OGG Vorbis Audio

* **Metadata:** No.
* **Detected as audio:** Yes (in mobile).
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** Yes.

ogg
~~~
Ogg Vorbis Compressed Audio

* **Metadata:** Yes.
* **Detected as audio:** Yes.
* **Audio playback in Telegram desktop:** Yes.
* **Audio playback in Telegram Android:** Yes.

opus
~~~~
Opus Audio

* **Metadata:** Yes.
* **Detected as audio:** Yes (in mobile).
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** Yes.

paf
~~~
PARIS Audio File Format

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

prc
~~~
Psion Record Format

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

pvf
~~~
Portable Voice Format

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

ra
~~
RealPlayer Audio

* **Metadata:** Yes.
* **Detected as audio:** Yes.
* **Audio playback in Telegram desktop:** Yes.
* **Audio playback in Telegram Android:** No.

sd2
~~~
Sound Designer 2

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

sln
~~~
Asterisk PBX

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

smp
~~~
Turtle Beach SampleVision File Format

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

snd
~~~
MS-DOS Audio

* **Metadata:** Yes.
* **Detected as audio:** Yes.
* **Audio playback in Telegram desktop:** Yes.
* **Audio playback in Telegram Android:** No.

sndr
~~~~
MS-DOS 90's Audio

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

sndt
~~~~
MS-DOS 90's Audio

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

sou
~~~
Solution User Options

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

sph
~~~
SPeech HEader Resources

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

spx
~~~
Speex Audio Compression Format

* **Metadata:** No.
* **Detected as audio:** Yes (in mobile).
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

tta
~~~
Free Lossless True Audio Codec

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

txw
~~~
Yamaha TX-16W sampler

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

vms
~~~
Dreamcast Visual Memory System File

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

voc
~~~
Creative Labs Audio File

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

vox
~~~
Dialogic Voice Audio File

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

w64
~~~
Sonic Foundry's 64-bit RIFF/WAV Format

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

wav
~~~
Waveform Audio File Format

* **Metadata:** Yes.
* **Detected as audio:** Yes.
* **Audio playback in Telegram desktop:** Yes.
* **Audio playback in Telegram Android:** Yes.

wma
~~~
Microsoft Windows Media Audio Format

* **Metadata:** Yes.
* **Detected as audio:** Yes.
* **Audio playback in Telegram desktop:** Yes.
* **Audio playback in Telegram Android:** No.

wv
~~
WavPack

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.

wve
~~~
Wondershare Filmora Project File

* **Metadata:** No.
* **Detected as audio:** No.
* **Audio playback in Telegram desktop:** No.
* **Audio playback in Telegram Android:** No.
