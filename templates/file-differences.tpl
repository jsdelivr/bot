In *{{project}}* between *{{previous-version}}* and *{{version}}* there was a change in file structure  
    ```diff
    {{#new-files}}
    + {{.}}
    {{/new-files}}
    {{#missing-files}}
    - {{.}}
    {{/missing-files}}
    ```