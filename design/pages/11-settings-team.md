# 11 — Settings / Team

**Route:** `/settings`
**Goal:** minimal workspace and team management — enough for a small production team, no more.

## Layout
- Tabs: **Workspace** (name, delete workspace), **Team** (invite by email, role: Owner/Editor/Viewer, pending invites list), **API** (view-only display confirming which Google Cloud project and Parallel account this workspace is connected to — useful for a judge inspecting the demo, and honest about what's powering the tool).

## States
- Invite sent: inline confirmation, not a toast that disappears before it's read.
- Removing a team member: a plain confirmation step naming exactly what will happen ("They'll lose access to all projects in this workspace immediately.").
