To rebase @{{user.login}} execute the following commands:

```shell
git reset --soft HEAD~{{commits}}
git commit -m "{{{title}}}"
git push --force
```

:dancers: 1... 2... 3... Good to go! :dancers: