# MSC4284 Policy Server Checker

> [!WARNING]
> This module is ***highly experimental*** and subject to breakage, change, and deprecation with no or limited
> notice. **Use at your own risk** (but let us know if there's bugs).

> [!CAUTION]
> This module automatically disables itself on May 21st, 2025. You should uninstall (or upgrade) it before then.
> Check the latest releases for changes to this date.

> [!IMPORTANT]
> Check for updates often as this module may change behaviour, or have its End of Life date above extended.

> [!WARNING]
> This module may have performance implications for your server, even after the End of Life date above.

A [Synapse](https://github.com/element-hq/synapse) spam checker module implementation for servers looking to opt in
early to [MSC4284](https://github.com/matrix-org/matrix-spec-proposals/pull/4284).

For communities which want added protection and auto-redaction, the module can also be configured to redact messages
which fail the policy server checks.

See the [matrix.org blog](https://matrix.org/blog/2025/04/introducing-policy-servers/) or
[MSC4284](https://github.com/matrix-org/matrix-spec-proposals/pull/4284) for more details.

## Installing

In your Synapse Python environment:

```bash
pip install git+https://github.com/element-hq/policyserv_spam_checker#egg=policy-server-checker
```

Then add the following to your `homeserver.yaml`:

```yaml
modules:
  - module: "policy_server.Checker"
    config:
      # Note: the module does all of its work in the background. The following configuration is
      # only needed for communities which *additionally* want auto-redaction.

      # If set, the user ID to issue redactions as in the room IDs listed below.
      fallback_user_id: "@abuse:matrix.org"
      # If the fallback_user_id is set above, these are the rooms where redactions will be sent
      # for events which fail the room's defined policy server checks.
      fallback_room_ids:
        - "!room:example.org"
        - "!another:example.org"
```

Synapse will need to be restarted to apply the changes. To modify the config, update accordingly and restart Synapse again.

## End of life

This module is expected to be incorporated into Synapse itself in short time, and will currently do a whole lot of nothing
on May 21st, 2025. New releases of the module may extend this date - check back often, and disable/uninstall the module if
the end of life date has passed.
