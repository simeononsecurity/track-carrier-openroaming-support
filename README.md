# track-carrier-openroaming-support

Tracks OpenRoaming Support Using NAPTR and SRV Lookups for every PLMNID listed on [mcc-mnc.com](https://www.mcc-mnc.com/)

Automatically updates every week using github actions.

[![Sponsor](https://img.shields.io/badge/Sponsor-Click%20Here-ff69b4)](https://github.com/sponsors/simeononsecurity)

The WBA also has a tool where you can check for these records manually [https://wballiance.com/OR/Tools/realm-check.html](https://wballiance.com/OR/Tools/realm-check.html)

<!-- Tables Start -->
## OpenRoaming Support Status

| Status                  | Percentage   |
|-------------------------|--------------|
| OpenRoaming Supported   | 0.20%        |
| OpenRoaming Unsupported | 99.80%       |

## Supported Carriers

| Network          | Country                  |   MCC |   MNC | Host              |   Port |
|------------------|--------------------------|-------|-------|-------------------|--------|
| Swisscom         | Switzerland              |   228 |    01 | test.idp.pwlan.ch |   2083 |
| AT&T Mobility    | United States of America |   310 |   150 | idp.3af521.net    |   2083 |
| Verizon Wireless | United States of America |   310 |   280 | idp.3af521.net    |   2083 |
| AT&T Mobility    | United States of America |   310 |   410 | idp.3af521.net    |   2083 |
| Limitless        | United States of America |   310 |   690 | idp.3af521.net    |   2083 |

> Note 310:280 is also AT&T, the used data set is wrong on that one.

## Realm Lookup Results

A few realms we've identified from public certificates, public documentation, and authentication attempts.

| Domain                                 | Host                         |   Port |
|----------------------------------------|------------------------------|--------|
| aka.xfinitymobile.com                  | idp.3af521.net               |   2083 |
| apple.openroaming.net                  | idp.openroaming.net          |   2083 |
| ciscoid.openroaming.net                | idp.openroaming.net          |   2083 |
| clus.openroaming.net                   | idp.openroaming.net          |   2083 |
| davidlloyd.openroaming.net             | idpeu.openroaming.net        |   2083 |
| delhaize.openroaming.net               | idpeu.openroaming.net        |   2083 |
| eu-sdk.openroaming.net                 | idpeu.openroaming.net        |   2083 |
| globalro.am                            | radsec.globalro.am           |   2083 |
| google.openroaming.net                 | idp.openroaming.net          |   2083 |
| idp.openroamingconnect.org             | idp.openroamingconnect.org   |   2083 |
| ironwifi.net                           | radsec.ironwifi.net          |   2084 |
| jwa.bemap.cityroam.jp                  | jpgw4.cityroam.jp            |   2083 |
| openroaming.goog                       | radsec.openroaming.goog      |   2083 |
| openroaming.securewifi.io              | idp.securewifi.io            |  20830 |
| or1.guglielmo.biz                      | or1.guglielmo.biz            |   2083 |
| orion.area120.com                      | radsec.orion.area120.com     |   2083 |
| prod.openroaming.wefi.com              | prod.openroaming.wefi.com    |   2083 |
| prod.premnet.wefi.com                  | prod.premnet.wefi.com        |   2083 |
| profile.guglielmo.biz                  | openroaming.guglielmo.biz    |   2083 |
| samsung.openroaming.net                | idp.openroaming.net          |   2083 |
| sdk.openroaming.net                    | idp.openroaming.net          |   2083 |
| securewifi.purple.ai                   | rad1-secure.purple.ai        |   2084 |
| test.orportal.org                      | test.orportal.org            |   2083 |
| tetrapi.pt                             | idp.openroaming.tetrapi.pt   |   2083 |
| tokyo.wi2.cityroam.jp                  | jpgw4.cityroam.jp            |   2083 |
| w-jp1.wi2.cityroam.jp                  | jpgw4.cityroam.jp            |   2083 |
| w-jp2.wi2.cityroam.jp                  | jpgw4.cityroam.jp            |   2083 |
| wayfiwireless.com                      | idp.wayfiwireless.com        |   2083 |
| wayru.io                               | radsec.wayru.io              |   2083 |
| wba.3af521.net                         | idp.3af521.net               |   2083 |
| wlan.mnc460.mcc313.pub.3gppnetwork.org | openroaming-proxy-1.mobi.com |   2083 |
| xfinitymobile.com                      | idp.3af521.net               |   2083 |
<!-- Tables End -->
