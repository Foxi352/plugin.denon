# AVR widget

# Supported macros
macro avr(id, gad_power, gad_vol, gad_volup, gad_voldown, gad_mute, gad_nowplaying, gad_station, gad_source, gad_sourceslist)
macro tone(id, gad_bass, gad_trebble)

## pages examples

~~~
	<div class="block">
		<div class="set-2" data-role="collapsible-set" data-theme="c" data-content-theme="a" data-mini="true">
			<div data-role="collapsible" data-collapsed="false">
				<h3>Denon AVR-1912</h3>
				{% import "widget_avr.html" as swa %}
				{{ swa.avr('EG.Stube.Denon', 'EG.Stube.Denon.Power', 'EG.Stube.Denon.Volume', 'EG.Stube.Denon.VolumeUp', 'EG.Stube.Denon.VolumeDown', 'EG.Stube.Denon.Mute', 'EG.Stube.Denon.NowPlaying', 'EG.Stube.Denon.Station', 'EG.Stube.Denon.Source', {'TV': 'TV', 'BD': 'BD', 'GAME': 'WII', 'IRADIO': 'IRADIO'}) }}
			</div>
			<div data-role="collapsible" data-collapsed="true">
				<h3>Settings</h3>
				{% import "widget_avr.html" as swa %}
				{{ swa.tone('EG.Stube.Denon.Tone', 'EG.Stube.Denon.Bass', 'EG.Stube.Denon.Trebble') }}
			</div>
		</div>
	</div>
    </blockquote>
~~~
