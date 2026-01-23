## Cómo publicar esta Wiki en GitHub

GitHub maneja la **Wiki** como un repositorio separado: `<repo>.wiki.git`. Este proyecto incluye las páginas en `wiki/` para que:

- queden versionadas junto al código, y
- se puedan copiar/sincronizar fácilmente a la Wiki oficial de GitHub.

### Opción A (recomendada): mantenerla in-repo

- Edita las páginas en `wiki/`
- En tu README o docs internas, enlaza a `wiki/Home.md`

### Opción B: publicar a la GitHub Wiki (repositorio separado)

1. Cloná la wiki del repo (en tu máquina):

```bash
git clone <REPO_URL>.wiki.git
```

2. Copiá el contenido de `wiki/` dentro del repo `.wiki.git` (manteniendo los nombres):
   - `Home.md`
   - `_Sidebar.md`
   - (resto de páginas)

3. Commit y push:

```bash
git add .
git commit -m "Update wiki"
git push
```

### Convención de nombres

- `Home.md` es la página principal.
- `_Sidebar.md` define el menú lateral.
- Los links en la wiki se escriben como `([Título](Nombre-De-Página))` sin extensión.

