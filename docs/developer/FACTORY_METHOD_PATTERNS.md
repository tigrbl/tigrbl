# Factory Method Patterns

Tigrbl uses five factory verbs with deliberately different meanings. The
functional form is canonical. A product classmethod may delegate to it when a
concrete product family owns the result. Specifications remain passive data:
`ColumnSpec`, `OpSpec`, `AppSpec`, `RouterSpec`, and `TableSpec` do not acquire
factory methods.

## Verb contract

| Verb | Meaning | Must not imply |
|---|---|---|
| `make` | Construct one concrete value. | registration or activation |
| `define` | Declare reusable specification configuration. | a running product |
| `derive` | Produce a new specification or product class from existing inputs. | mutation of the inputs |
| `provide` | Normalize and validate an existing specification source. | construction of unrelated state |
| `activate` | Bind a table specification into executable operations. | declarative purity |

Choose the verb from the result and effect, not from naming preference. Do not
use `make` for binding, `define` for runtime work, or `activate` for a pure
transformation.

## Supported forms

The canonical functions own behavior. The classmethods are thin, late-imported
delegates and must return the same category of result.

| Verb | Functional form | Classmethod form | Ordinary method form |
|---|---|---|---|
| `make` | `makeColumn(...)`, `makeVirtualColumn(...)`, `makeOp(...)` | `Column.make(...)`, `Column.make_virtual(...)`, `Op.make(...)` | none; there is no meaningful receiver |
| `define` | `defineAppSpec(...)`, `defineRouterSpec(...)`, `defineTableSpec(...)` | `TigrblApp.define(...)`, `Router.define(...)`, `Table.define(...)` | none; definitions are not instance state |
| `derive` | `deriveApp(...)`, `deriveRouter(...)`, `deriveTableSpec(...)`, `deriveTable(...)` | `TigrblApp.derive(...)`, `Router.derive(...)`, `Table.derive(...)`, `Table.derive_class(...)` | none; source inputs are explicit |
| `provide` | `provideTableSpec(source)` | `Table.provide(source)` | only on products with a real provider receiver; not added for parity |
| `activate` | `activateTableSpec(source)` | `Table.activate(source)` | none; a spec is input, never the owner |

### `make`

```python
column = makeColumn(nullable=False)       # functional, canonical
column = Column.make(nullable=False)      # classmethod delegate
operation = Op.make(alias="inspect")     # classmethod delegate
```

There is intentionally no `column.make()`: an existing column is not the
receiver for constructing a different column.

### `define`

```python
app_spec = defineAppSpec(title="Inventory")
app_spec = TigrblApp.define(title="Inventory")

router_spec = Router.define(name="inventory")
table_spec = Table.define(ops=("create", "read"))
```

The returned objects are specification classes. Defining them performs no
activation.

### `derive`

```python
app_type = deriveApp(title="Inventory")
app_type = TigrblApp.derive(title="Inventory")

table_spec = deriveTableSpec(Widget, ops=("read",))
table_spec = Table.derive(Widget, ops=("read",))
table_type = Table.derive_class(Widget, ops=("read",))
```

`Table.derive` is the specification-producing form; `Table.derive_class` names
the distinct class-producing result. `deriveTableSpec` may compose a reusable
definition using `spec=...`; explicit arguments extend or override the
collected definition without mutating either source.

### `provide`

```python
normalized = provideTableSpec(table_spec)
normalized = Table.provide(table_spec)
```

An ordinary `.provide()` method is appropriate only when an instantiated
provider genuinely owns resources or policy used by the operation. It is not
added to a specification merely to complete a naming matrix.

### `activate`

```python
operations = activateTableSpec(table_spec)
operations = Table.activate(table_spec)
```

Activation is the effectful boundary. Keep definition and derivation before
it, and do not put `.activate()` on `TableSpec`.

## Implementation rules

1. Put algorithms in `tigrbl_concrete.factories`; product classmethods only
   delegate.
2. Use late imports inside delegates to preserve package direction and avoid
   import cycles.
3. Keep specifications passive and immutable-by-convention as factory inputs.
4. Record every public surface and its canonical target in
   `factory_surfaces.json`.
5. Test functional/classmethod result equivalence, descriptor shape, source
   non-mutation, verb effects, and discovery coverage.
6. Do not add an ordinary method unless the receiver contributes meaningful
   state to the operation.
