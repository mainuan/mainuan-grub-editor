# Internacionalização — mainuan-grub-editor

Contrato comum: `docs/03-arquitetura-i18n-kde.md` do repositório `mainuan`.

## Resumo

| Item | Valor |
|---|---|
| Domínio gettext | `mainuan-grub-editor` |
| Idioma-fonte (msgid) | inglês (sem catálogo `en`) |
| POT | `locale/mainuan-grub-editor.pot` |
| Catálogos | `locale/<lang>/LC_MESSAGES/mainuan-grub-editor.po` (layout histórico, mantido) |
| Idiomas compilados | `po/LINGUAS` (de es fr it pt pt_BR ro ru) |
| Fontes extraídas | `po/POTFILES.in` |
| Configuração | `po/i18n.conf` (`POT`/`PO_NAME` apontam para `locale/`) |
| `.desktop` | modelo `assets/org.mainuan.grubeditor.desktop.in`, gerado no build |
| Instalação | `/usr/share/locale/<lang>/LC_MESSAGES/mainuan-grub-editor.mo` |

Os `.mo` não são mais versionados: são gerados por `packaging/build-deb.sh`
(ou por `po/i18n.sh compile locale` para executar a partir do código-fonte).

## Execução

`core/i18n_manager.py` usa `gettext.translation(domain, localedir,
fallback=True)`, que resolve o idioma por `LANGUAGE`, `LC_ALL`,
`LC_MESSAGES` e `LANG`. Não há lista fixa de idiomas: qualquer catálogo
instalado é usado; sem catálogo correspondente aparece o msgid em inglês
(antes o fallback era espanhol). `pt_BR` e `pt` são catálogos separados.

Diretório dos catálogos (`default_locale_dir()`):

1. `$MAINUAN_GRUB_EDITOR_LOCALEDIR`, se definido;
2. `locale/` do checkout, se contiver `.mo` compilados;
3. senão, o diretório do sistema (`/usr/share/locale`).

O aplicativo roda como root via `pkexec`, que limpa o ambiente; por isso
`debian/mainuan-grub-editor` e `main.py` repassam `LANG`, `LANGUAGE`,
`LC_ALL` e `LC_MESSAGES` ao processo elevado.

A API pública (`_`, `ngettext`, `set_language`, `get_current_language`,
`initialize_i18n`, `get_i18n_manager`, métodos de `I18nManager`) foi mantida;
`N_()` foi acrescentado para marcar constantes (`APP_NAME`).

## Tarefas

```sh
po/i18n.sh extract        # regenera locale/mainuan-grub-editor.pot
po/i18n.sh update         # msgmerge em todos os idiomas de po/LINGUAS
po/i18n.sh check-pot      # falha se o POT estiver desatualizado
po/i18n.sh validate       # msgfmt --check + placeholders
po/i18n.sh coverage
po/i18n.sh compile locale # .mo ao lado dos .po, para rodar do checkout
mkdir -p locale/<lang>/LC_MESSAGES && po/i18n.sh add <lang>   # novo idioma
```

## Testes

```sh
python3 -m unittest discover -s tests -v
```

`tests/test_i18n.py` compila os catálogos num diretório temporário e verifica
`LANGUAGE`/`LANG`/`LC_ALL`, a separação `pt`/`pt_BR`, o fallback inglês e a
API pública. Com display disponível, monta widgets reais (`GeneralView`) sem
mostrar janela; sem display o teste é pulado.

## Pendências

* `debian/org.mainuan.grubeditor.metainfo.xml` ainda tem traduções escritas à
  mão (`xml:lang`), sem `pt_BR`. Convertê-lo para `msgfmt --xml` exige
  reestruturar as notas de versão (hoje com `<p xml:lang="en">` sem texto
  base); ficou fora desta etapa.
* Cabeçalhos dos catálogos herdados citam "Soplos GRUB Editor" (origem do
  projeto); mantidos como crédito.
