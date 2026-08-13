# CMS export mappings

These offline examples map common vendor exports into the stable
`contentgraph.cms-export/v1` contract. They are data-shape examples, not network
clients: export data through the vendor's supported tooling, redact private
fields, then emit only `id`, `title`, `content`, and the optional portable fields
shown here.

| Vendor | Typical source fields | ContentGraph fields |
| --- | --- | --- |
| WordPress | `id`, `link`, `slug`, `title.rendered`, `content.rendered`, `modified_gmt`, `status` | `id`, `url`, `canonical`, `title`, `content`, `updated_at`, `status` |
| Contentful | `sys.id`, `fields.slug`, localized `fields.title` and rich text, `sys.updatedAt` | same stable output fields |
| Sanity | `_id`, `slug.current`, `title`, Portable Text, `_updatedAt` | same stable output fields |
| Drupal | UUID/NID, path alias, title, rendered body, changed timestamp, moderation state | same stable output fields |
| Generic SQL | primary key, canonical URL, title, rendered/text body, update timestamp, state | same stable output fields |

Every example is validated and ingested without network access by
`tests/contentgraph_tests.kujo`.
