# Template Recommendations

This document tracks the next steps for making the scaffold a stronger reusable server template.

## Recommended access key shape

```text
action/path_to_object
```

Examples:

```text
read/users/*
write/users/*
delete/users/*
manage/org/acme/project/**
```

The first segment is the action. The rest is the object path.
