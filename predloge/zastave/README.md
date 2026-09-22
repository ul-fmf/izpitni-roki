# Zastave

Datoteke `sl.svg`, `en.svg` in `de.svg` so prevzete iz projekta
[flag-icons](https://github.com/lipis/flag-icons) (mapa `flags/4x3`, datoteke
`si.svg`, `gb.svg` in `de.svg`) in so objavljene pod licenco MIT:

> Copyright (c) 2013 Panayiotis Lipiridis
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.

Datotek namenoma ne spreminjamo, da jih je mogoče osvežiti s preprostim
prenosom. Velikost in okvir jima da `out/dodatni.css` prek ovoja
`span.zastava`, dostopno ime jezika pa doda `predloge/jezik_povezava.html`.

Osvežitev:

```
curl -o predloge/zastave/sl.svg https://raw.githubusercontent.com/lipis/flag-icons/main/flags/4x3/si.svg
curl -o predloge/zastave/en.svg https://raw.githubusercontent.com/lipis/flag-icons/main/flags/4x3/gb.svg
curl -o predloge/zastave/de.svg https://raw.githubusercontent.com/lipis/flag-icons/main/flags/4x3/de.svg
```
