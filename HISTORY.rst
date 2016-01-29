Changelog
=========


1.1.3 (2016-01-29)
----------------

- Add support for later postgres versions.
  [MatthewWilkes]


1.1.2 (2016-01-29)
----------------

- Add TextField to the types that can be sanitised.
  [MatthewWilkes]


1.1.1 (2016-01-29)
----------------

- Fix a bug in 1.1 that meant the additional sensitive fields on model setting was an all-or-nothing affair.
  [MatthewWilkes]


1.1 (2016-01-29)
----------------

- Allow specification of additional model fields to treat as sensitive using django settings.
  [MatthewWilkes]


1.0 (2016-01-29)
----------------

- Initial release, basic support for built in field types, especially on postgres. Limited sqlite support.
  [MatthewWilkes]
