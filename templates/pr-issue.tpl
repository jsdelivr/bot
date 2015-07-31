It looks like you want to contribute to `jsdelivr/jsdelivr`, @{{login}}, however there seems to be some issues with your pull request. See [contributing](https://github.com/jsdelivr/jsdelivr/blob/master/CONTRIBUTING.md) for help amending your PR...

{{#has-warnings}}
- There are some fundamental issues with your PR :no_good:  
    {{#warnings}}
    - {{{.}}}
    {{/warnings}}
{{/has-warnings}}
{{#has-ini-issues}}
- Looks like the `info.ini` or `update.json` has some problems
    {{#info-issues}}
    - {{{.}}}
    {{/info-issues}}
{{/has-ini-issues}}
{{#has-file-issues}}
- Might be nothing but I have some concerns about the files in your submission...  
    {{#file-issues}}
    - {{{.}}}
    {{/file-issues}}
{{/has-file-issues}}
{{#has-version-issues}}
- We try to keep the file structure as consistent as possible between versions; there were some changes in file structure from previous versions...  
    {{#version-issues}}
    - {{{.}}}
    {{/version-issues}}
{{/has-version-issues}}
  
----------
<sup>Thanks again for contributing.. If you think this review was wrong/unfair/etc. submit a bug on [the bot's repo](https://github.com/jsdelivr/bot)</sup>  
*{{qotd}}*
