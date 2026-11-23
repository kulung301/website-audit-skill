# Security policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 1.0.x   | Yes       |

## Reporting a problem with this skill

- For ordinary bugs, open a GitHub issue.
- For anything sensitive — for example a way to make the scripts contact
  unintended hosts, bypass the SSRF guard, or leak data from the machine
  running them — please do not post details publicly. Use GitHub's private
  vulnerability reporting on this repository if it is offered, or open an
  issue asking for a private channel without including the details.

## Scope notes

- This skill is passive by design: it sends ordinary GET/HEAD requests to a
  target the user names, caps its volume, and refuses private or loopback
  addresses unless the user explicitly allows them for a site they own.
- Findings about a target website belong to that site's owner (or its bug
  bounty program), not to this repository. This policy covers the skill's
  own code only.
