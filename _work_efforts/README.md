# Work Efforts

This directory uses the **Johnny Decimal** system for organizing work efforts and project documentation.

## System Overview

```
_work_efforts_/
├── 00-09_admin/              # Administration & Meta
│   ├── 00_organization/      # System organization, indexes
│   └── 01_devlog/            # Development logs
├── 10-19_projects/           # Active Projects
│   ├── 10_current/           # Currently active work
│   └── 11_backlog/           # Planned future work
├── 20-29_learning/           # Learning & Tutorials
├── 30-39_experiments/        # Experiments & Prototypes
├── 40-49_utilities/          # Scripts & Utilities
└── 50-59_archive/            # Completed/Archived work
```

## Numbering Convention

| Range   | Category              | Purpose                          |
|---------|----------------------|----------------------------------|
| 00-09   | Admin & Meta         | Organization, logs, indexes      |
| 10-19   | Projects             | Active and planned projects      |
| 20-29   | Learning             | Tutorials, courses, practice     |
| 30-39   | Experiments          | Prototypes, R&D, explorations    |
| 40-49   | Utilities            | Scripts, tools, automation       |
| 50-59   | Archive              | Completed or paused work         |
| 60-99   | Reserved             | Future expansion                 |

## Document Naming

Documents follow the pattern: `XX.YY_descriptive_name.md`

- `XX` = Category number (00-99)
- `YY` = Document number within category (00-99)
- `00` is always the index file

Example: `10.01_api_integration_project.md`

## Creating a New Work Effort

1. Identify the appropriate category (00-59)
2. Find the next available document number
3. Create the file using the template below
4. Update the category's index file (`XX.00_index.md`)
5. Log the creation in the devlog

## Work Effort Template

```markdown
# Work Effort: [Title]

## Status: [In Progress/Completed/On Hold/Cancelled]
**Started:** YYYY-MM-DD HH:MM
**Last Updated:** YYYY-MM-DD HH:MM

## Objective
[Brief description of the work effort's goal]

## Tasks
- [ ] Task 1
- [ ] Task 2

## Progress
- [List of completed items]

## Next Steps
1. [Next immediate action]
2. [Following action]

## Notes
- [Important notes or considerations]
```

## Quick Commands

Create a new work effort:
1. Copy template above
2. Save to appropriate category folder
3. Update index and devlog

## Links

- [[00-09_admin/00_organization/00.00_index|Organization Index]]
- [[00-09_admin/01_devlog/00.00_index|Devlog Index]]

