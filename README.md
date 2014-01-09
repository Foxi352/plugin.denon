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
			[[[[Volume]]]]
				type = num
				visu_acl = rw
				denon_send = volume
				enforce_updates = on
</pre>
