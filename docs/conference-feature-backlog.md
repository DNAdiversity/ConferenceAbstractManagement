# Conference Feature Backlog

## Current Git/Repo Status

As of April 16, 2026, the repository's default branch is `master`, not `main`.

- `master` is at `6afd8c32b1c691b0b83fc40ec9fb29da1b44e3e2` from `2026-04-15 05:49:42 -0400`
- `add-license-1` is at `99e9f95b0029224498e3ad486cad95ea41f54070` from `2026-04-15 05:48:36 -0400`
- `master` already contains the historical merge of `add-license-1`

The modern Django source is present and active on `master`. Work in this memo should be treated as the forward plan for the `modern_cam` application.

## Implemented In This Pass

These items are now in the app on `master`:

1. Submission receipt and audit trail
   - immutable submission snapshots
   - receipt view tied to the submitted payload
   - visible status/event history on submission detail pages
   - admin visibility into snapshot history

2. Reliable confirmation and fallback notifications
   - automatic submission receipt email on final submit
   - resend receipt action from the submission record
   - notification log stored per submission

3. Co-author approval certification
   - submitter must explicitly certify that all authors approved before final submission
   - certification is recorded in the submission and receipt snapshot

4. Deadline clarity and leaner submission UX
   - timezone-aware deadline ribbon across the app
   - submit button lock after the submission window closes
   - live abstract word count
   - compact reviewer-style preview while drafting

## What Other Systems Already Do

### Reviewer Assignment and Review Management

From official docs for Microsoft CMT, Oxford Abstracts, and ConfTool:

- reviewer bidding
- topic and expertise matching
- conflict-of-interest checks
- auto-assignment with reviewer load balancing
- reassignment of incomplete or overdue reviews
- reviewer refusal flows
- configurable rubrics and scoring ranges
- inline comments on submissions
- rebuttals and author-visible comments
- program-committee discussion around submissions

### Admin and Decision Workflows

From official docs for Oxford Abstracts and ConfTool:

- bulk decisions
- editable decision tables
- filtered committee views by category/topic
- bulk email from submission tables
- review and submission tables with flexible columns, filters, and exports
- admin ability to edit/complete reviews on behalf of reviewers

### Programme and On-Site Operations

From official docs for Ex Ordo and ConfTool:

- agenda/programme builder
- presentation codes / universal IDs
- poster board numbering tied to schedule items
- exports for PDF, Word, Excel, JSON
- attendee-facing programme views and personal agendas

## What Researchers Complain About

### Direct Complaints or Near-Complaints from Researcher Social Spaces

From Reddit and similar researcher-facing communities:

- submissions marked incomplete even after confirmation email
- missing or unreliable confirmation emails
- confusing per-section word limits and rigid submission structures
- co-author approval and authorship disputes
- supervisors submitting abstracts without notifying junior researchers
- uncertainty about whether all co-authors approved the submission

### Strong Inferences from Social Signals

This is an inference, not a direct quote-based finding:

- repeated conference deadline extensions on Bluesky and X suggest that submission flows are often too confusing, too time-consuming, or too easy to abandon near deadline

## Recommended Feature Set

### P0: Trust, Safety, and Submission Reliability

These directly address the biggest user anxieties.

1. Submission receipt and audit trail
   - generate a permanent receipt on submit
   - store the exact submitted payload
   - show status history with timestamps
   - let users download a submission confirmation PDF

2. Reliable confirmation and fallback notifications
   - confirmation email plus in-app receipt
   - resend confirmation button
   - admin delivery status for submission emails

3. Co-author approval workflow
   - optional co-author acknowledgement emails
   - required presenter confirmation for final submission
   - admin-visible log of who approved what

4. Deadline clarity
   - exact deadline with timezone
   - warning banners as deadline approaches
   - lock behavior clearly explained before submit

### P1: Better Submission UX

These reduce drop-off and support higher-quality abstracts.

5. Live word counts and section counts
   - total count and per-field count
   - show whether references/keywords count or not
   - pre-submit validation summary

6. Autosave and draft recovery
   - timed autosave
   - dirty-state warnings before leaving
   - restore last draft snapshot

7. Submission preview
   - reviewer-style preview before final submit
   - printable abstract preview

8. Smarter form design
   - conditional fields by presentation type
   - optional "advanced metadata" drawer instead of long static forms
   - save-and-continue later by section

### P1: Reviewer and Chair Tools

These are table-stakes in stronger platforms.

9. Reviewer bidding
   - eager / willing / not willing
   - reviewer-entered conflicts
   - assignment recommendations that combine topic fit, bids, and workload

10. Stronger conflict-of-interest handling
   - email-domain conflict check
   - institution conflict check
   - co-author/reviewer manual COI override

11. Rebuttal and revision rounds
   - allow authors to respond to reviews
   - allow revision-request decisions
   - preserve version history between rounds

12. Inline reviewer comments
   - anchored comments on specific text passages
   - side-by-side diff between original and revised abstract

13. Committee discussion and meta-review
   - internal chair discussion thread
   - meta-review / final recommendation
   - best abstract / prize nomination

### P2: Programme Builder and Presenter Operations

These move the system from "submission tool" to "conference operating system."

14. Rich agenda builder
   - drag-and-drop scheduling
   - room and chair assignment
   - slot duration templates
   - conflict checking for presenters and rooms

15. Presentation codes and poster numbering
   - stable presentation IDs for schedule, exports, signage, and poster boards

16. Presenter readiness workflow
   - acceptance confirmation
   - upload slides/poster
   - AV requirements
   - remote / in-person designation

17. Public and attendee views
   - searchable programme
   - speaker cards
   - personal agenda bookmarks

### P2: Admin Reporting and Ops

18. Bulk communications
   - message submitters by status/category
   - message reviewers by overdue/open load
   - send decision letters from templates

19. Operational exports
   - abstract book export
   - reviewer workbook export
   - session chair briefing export
   - poster hall map export

20. Data quality controls
   - duplicate abstract detection
   - missing presenter / missing registration flags
   - orphaned submissions / incomplete author list flags

## Best Next Implementation Order

Given the missing source-tree blocker, the next implementation sequence should be:

1. Restore or rebuild the `modern_cam` Django source into tracked files
2. Add submission receipts + audit trail
3. Add reliable confirmation/resend flow
4. Add live word counts and preview
5. Add co-author approval / presenter confirmation
6. Add reviewer bidding and stronger COI checks
7. Add rebuttal / revision rounds
8. Add drag-and-drop agenda builder with presentation codes

## Sources

Official product / help sources:

- Microsoft CMT reviewer bidding: https://cmt3.research.microsoft.com/docs/help/reviewer/reviewer-bidding.html
- Oxford Abstracts reviewer assignment: https://help.oxfordabstracts.com/knowledge/assigning-and-unassigning-a-submission-to-a-reviewer
- Oxford Abstracts inline comments for submitters: https://help.oxfordabstracts.com/knowledge/draft-submitters-inline-comments
- Oxford Abstracts reviewer recruitment/categories: https://help.oxfordabstracts.com/knowledge/how-to-create-the-reviewer-form-and-assign-reviewers
- Oxford Abstracts submission controls: https://help.oxfordabstracts.com/knowledge/open-and-close-submissions-/-call-for-abstracts
- Oxford Abstracts submissions table: https://help.oxfordabstracts.com/knowledge/the-submissions-table
- Oxford Abstracts decisions table: https://help.oxfordabstracts.com/knowledge/the-decisions-table
- Oxford Abstracts reviewer inline comments/diffing: https://help.oxfordabstracts.com/knowledge/reviewers-leaving-inline-comments
- ConfTool features: https://www.conftool.net/en/features.html
- Ex Ordo programme / presentation codes: https://www.exordo.com/blog/precision-planning-automated-integrity

Researcher social / community signals:

- Incomplete portal despite confirmation email: https://www.reddit.com/r/GradSchool/comments/147qco4/applied_to_my_first_conference_incomplete/
- Missing confirmation emails: https://www.reddit.com/r/REU/comments/1j3lusf/anyone_else_have_issues_receiving_confirmation/
- Co-author approval concerns: https://www.reddit.com/r/AskAcademia/comments/1atcpjc/is_it_wrong_to_send_an_abstract_for_a_conference/
- Authorship / notification dispute: https://www.reddit.com/r/academia/comments/1sh0u0v/my_supervisor_submitted_my_conference_abstract/
- Word-limit / form-structure friction: https://www.reddit.com/r/AskAcademia/comments/1gq3rxc/are_conferences_lenient_with_abstract_deadlines/
- Small abstract / reference squeeze: https://www.reddit.com/r/labrats/comments/yarfox/help_needed_abstract_submission_for_a_conference/
