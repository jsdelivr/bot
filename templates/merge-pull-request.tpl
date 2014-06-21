Squash and merge pull request #{{number}} from {{user.login}}/{{head.ref}}
{{title}}
{{description}}
Closes #{{number}}

Squashed Commits:

{{#iter_commits}}
{{last_modified}}
    {{#author}}{{login}}{{/author}} committed: {{message}}
{{/iter_commits}}