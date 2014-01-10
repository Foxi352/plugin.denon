# Denon

# Requirements

A properly installed and configured Logitech Media Server is required.

## Supported Hardware

Tested with:
* Denon AVR-1912

Should work with other Denon and some Marantz receivers - please let me know!

# Configuration

## plugin.conf

<pre>
[denon]
    class_name = Denon
    class_path = plugins.denon
    host = &lt;ip&gt;
#   port = &lt;port&gt;
</pre>

Description of the attributes:

* __host__: IP or hostname of the AVR
* __port__: Port number of the Logitech Media Server if not 23

## items.conf

<pre>
[[[Denon]]]
	[[[[Power]]]]
		type = bool
		visu_acl = rw
		denon_send = power
		enforce_updates = on
	[[[[Mute]]]]
		type = bool
		visu_acl = rw
		denon_send = mute
		enforce_updates = on
	[[[[Volume]]]]
		type = num
		visu_acl = rw
		denon_send = volume
		enforce_updates = on
	[[[[VolumeUp]]]]
		type = bool
		visu_acl = rw
		denon_send = volume+
		enforce_updates = on
	[[[[VolumeDown]]]]
		type = bool
		visu_acl = rw
		denon_send = volume-
		enforce_updates = on
</pre>

## pages Beispiele

<pre>
{{ basic.slider('slider1', 'EG.Stube.Denon.Volume', 0, 99, 1) }}
{{ basic.switch('switch1', 'EG.Stube.Denon.Power', icon1~'audio_audio.png', icon0~'audio_audio.png') }}  Verstärker
{{ basic.switch('switch2', 'EG.Stube.Denon.Mute', icon1~'audio_volume_mute.png', icon0~'audio_volume_mute.png') }}  Mute
{{ basic.switch('switch3', 'EG.Stube.Denon.VolumeDown', icon0~'control_minus.svg', icon0~'control_minus.svg') }}  Vol-
{{ basic.switch('switch4', 'EG.Stube.Denon.VolumeUp', icon0~'control_plus.svg', icon0~'control_plus.svg') }}  Vol+
</pre>