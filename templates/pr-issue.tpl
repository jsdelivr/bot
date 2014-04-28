Whooa, alright @{{login}} thanks for the contibuting and everythin', but it seems theres some issues you and me should sort out...

{{#has-warnings}}
- Please see [contributing](https://github.com/jsdelivr/jsdelivr#file-structure) before fixing your PR...  
    {{#warnings}}
    - {{.}}
    {{/warnings}}
{{/has-warnings}}
{{#has-ini-issues}}
- Looks like the `info.ini` has a few problems
    {{#info-issues}}
    - {{.}}
    {{/info-issues}}
{{/has-ini-issues}}
{{#has-file-issues}}
- Might be nothing but I have some concerns about the files in your submission...  
    {{#file-issues}}
    - {{.}}
    {{/file-issues}}
{{/has-file-issues}}
{{#has-version-issues}}
- There were some changes in some of the versions file structure from the previous version...  
    {{#version-issues}}
    - {{{.}}}
    {{/version-issues}}
{{/has-version-issues}}
----------
<sup>Thanks again for contributing.. If you think this review was wrong/unfair/etc. submit a bug on [the bot's repo](https://github.com/jsdelivr/bot)</sup>
{{qotd}}
