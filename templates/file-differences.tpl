In *{{project}}* between *{{previous-version.version}}* and *{{version.version}}* there was a change in file structure  
    ```diff
    {{#new-files}}
    + {{.}}
    {{/new-files}}
    {{#missing-files}}
    - {{.}}
    {{/missing-files}}
    ```