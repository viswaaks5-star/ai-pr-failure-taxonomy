# PR 118624 [CLOSED] — Add headings to GitHub pull request template.
AUTHOR: allenwp

## BODY
**Superseded by https://github.com/godotengine/godot/pull/118855**.

<!--
Please target the `master` branch. We will take care of backporting relevant fixes to older versions.

Before submitting, please read our checklist for new contributors:
https://contributing.godotengine.org/en/latest/engine/introduction.html#checklist-for-new-contributors
-->

### What problem(s) does this PR solve?

<!--
If the problems are described in an existing issue or proposal, you may link to them here. Use closing keywords if this PR closes the issue or proposal: https://docs.github.com/articles/closing-issues-using-keywords
-->

1. During PR review, especially in team meetings, it can take too much time to understand the root problem that a PR aims to solve.
2. During PR review, it is sometimes difficult to understand the rationale that was used for changes. This is especially a problem when an incorrect assumption is made by the reviewer regarding why a change was necessary.
3. PR authors who have not recently read the updated contributing docs may be unaware that they must now disclose their use of AI tools.
4. PR authors may assume that PR review will be extremely thorough and will catch any mistakes or sub-optimal decisions that were made in the PR, even when the PR author is aware of areas that may have mistakes or sub-optimal decisions. But, in practice, reviewers are left unaware of what specific parts of a PR might need special attention, making the review process more difficult and sometimes more error prone.
5. PR authors may desire and assume and that a review will initiate discussion over a technical detail that is relevant to the review, but the discussion will never happen because the technical detail was never brought up.

### What is the rationale for the approach used in this PR?

<!--
Providing a rationale is optional and may be omitted for simple PRs.
-->

This PR adds headings to the pull request template that prompt the PR author to answer some basic questions about their PR. The headings that I have chosen are designed primarily to improve the process for reviewing PRs.

By having standard headings for all new PRs, it will become much faster for reviewers to understand the PR in the ways that are necessary for a good and thorough review.

By asking the PR author to provide the problem that their PR reviews, it reinforces the Godot way of making changes: [The problem always comes first](https://contributing.godotengine.org/en/latest/engine/guidelines/best_practices.html#best-practices).

I have been trialing this new template on a number of my PRs. You can take a look and see how it plays out in practice on the following PRs:

1. https://github.com/godotengine/godot/pull/117754
2. https://github.com/godotengine/godot/pull/117800
3. https://github.com/godotengine/godot/pull/117837
4. https://github.com/godotengine/godot/pull/117913
5. https://github.com/godotengine/godot/pull/118076
6. https://github.com/godotengine/godot/pull/118079
7. https://github.com/godotengine/godot/pull/118083
9. https://github.com/godotengine/godot/pull/118355
10. https://github.com/godotengine/godot-docs/pull/11920
11. https://github.com/godotengine/godot/pull/117537
12. https://github.com/godotengine/godot/pull/118692
13. https://github.com/godotengine/godot-docs/pull/11931

Note that in my initial draft of this template, I also added the heading: "Does this PR include any additional changes beyond those required to solve these problems?". I later chose to remove this heading because it was often empty and it felt like it clashed with the first "What problem(s) does this PR solve?" heading.

As an anecdote: After attending many core and rendering team meetings, I have found that it is somewhat common for PR review to spend 10 or 15 minutes discussing a PR before Clay finally steps in and asks "What problem is this PR even aiming to solve?" and then we realize immediately that all of our talk was pointless because the PR doesn't do a good job of solving that problem or tries to do more than is necessary to actually solve this problem. My goal with this change to the PR template is that this waste of time will be avoided because all reviewers will be brought up to speed on what problem a PR solves as the first step in the review process.

### Was AI used to create any part of this PR?

<!--
The Godot project requires AI-assisted contributions to be disclosed. You can find out more about this policy in the docs: https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions
-->

No.

### Are there any parts of this PR that you are uncertain of or require special attention from reviewers?

Although I have included a heading for disclosing use of AI, this is the least important part of this PR to me personally. I'm fine with omitting this heading entirely and leaving it to a separate PR if there is any strong pushback or a large amount more work will be needed before this sort of thing can be merged into `master`.

## COMMENTS
--- DeanLemans:
This helps for larger PR, but It ups the barier of entry for new contributors and small PR.
If every PR has the same sections, people will start writing low effort text.(or just not do it)

I see 2 solutions (that i see, probbly more):

- make some sections optional for (small) PRs.
- strip this down to only the 'What problem(s) does this PR solve?'

--- allenwp:
> * make some sections optional for (small) PRs.

The second section is explicitly marked as optional in the comment text. Had you seen this yet?

--- allenwp:
> This helps for larger PR, but It ups the barier of entry for new contributors and small PR.
> If every PR has the same sections, people will start writing low effort text.(or just not do it)

Here is an example of what I expect this template to look like with a smaller PR: https://github.com/godotengine/godot/pull/118355

The second section could be omitted entirely if the PR author chooses, as mentioned in the comment for that section. I'm not sure that it would, in practice, increase the barrier to entry for new contributors or that there would be a problem with authors simply writing "No." in response to the final two sections.

--- DeanLemans:
Oh wow, idk how i missed that, ~~in that case i think 'What problem(s) does this PR solve?' Should be moved up.(almost to the top, as to inform the contributor that they should write the issue with that in mind)~~

~~And still think that this creates to much clutter/boilerplate for creating an issue, so in my opinion some sentaces should be removed/shortend/optimized.~~

Wait im an idiot, i got the bug report template and pr template parialy mixed up.

--- dagarsar:
> This helps for larger PR, but It ups the barier of entry for new contributors and small PR. If every PR has the same sections, people will start writing low effort text.(or just not do it)

I would argue that it helps new contributors break the barrier to entry. It helps new contributors in facilitating the review process, which is very often a hard place for a new contributor to stay in, particularly if it takes a long time or if there are many questions asked which are "obvious" for a PR author but not conveyed in the best way to a PR reviewer.


--- blueskythlikesclouds:
Maybe it's because English is not my native language, but the "What is the rationale for the approach used in this PR?" heading threw me off a bit. Maybe a more casual tone would work better?

--- allenwp:
> Maybe it's because English is not my native language, but the "What is the rationale for the approach used in this PR?" heading threw me off a bit. Maybe a more casual tone would work better?

This makes sense.

I'm interested in hearing suggestions. Of importance is the distinction between the PR's description and the rationale. The description text is included in the commit message, which maps to the title and initial body text of the PR -- the rationale section is not intended to duplicate the commit description/summary. Instead, it is a place for the PR author to provide an explanation of why they chose to author the PR the way that they did. Said differently, a place for them to provide their rationale.

For examples of what this section aims to get at, please take a look at the examples I listed in the rationale of this PR.

--- vaner-org:
To me, this reads simply like
1. **"what is the problem?"** - description of objective problem as you see it, or confirmed issue/adequately consensused proposal, should warn of the importance of the latter
2. **"how did you solve it, and why do it this way?"** - what motivated your solution, opportunity to explain your implementation and set yourself apart against competing PRs, if any
4. **"did you really?"** - or did your computer do it for you, be honest
5. **"anything else?"** - special notes

It could be as simple as this. Obviously it shouldn't. But it could!

In terms of what the current phrasing is specifically trying to elicit, some thoughts, they might be way off: in a codebase as expansive as this, most (good or incremental) solutions are going to be as adherent as possible to conventions already, so the "rationale" more than often than not is "I took the path I thought I was supposed to, to do what I wanted to." It's only when uncharted territory is entered that this question _really_ gets what it's fishing for, but if someone does venture there I'm sure they'd want to pretty it up and show it off anyway, as in some of the longer examples provided. I know I have.

--- allenwp:
Yeah, I think I like the suggestion for something more like "how did you solve it, and why do it this way?" I think this is a more clear way of communicating what I was trying to get at with my "What is the rationale for the approach used in this PR?" heading.

I'll revisit this soon and update that heading to look a little more like that.

--- allenwp:
Thinking more about the "how did you solve it" part of the "how did you solve it, and why do it this way?" suggestion…

My initial thought with this section was to provide an explanation of “why” and I think adding in a description of “how” is problematic because the changes of the PR already explain the “how” in perfectly accurate detail. So writing “how” text in the PR would probably be unnecessary/unhelpful and even misleading to reviewers if any mistakes are made when writing this.

So instead of “What is the rationale for the approach used in this PR?” I think the rewording should be something more like: “Why solve them this way?”

edit: or maybe better phrasing would be: “Why use this approach?” because it avoids the awkwardness of singular vs plural problem(s). Or maybe “Why use this solution?”

--- allenwp:
The other wrinkle to this is that a PR sometimes includes changes that are not directly related to solving the problem, such as refactoring. This section is intended to prompt the author to explain their reasoning for these sorts of changes.

So this section is the “rationale for the PR’s changes”: both why an approach was used for solving the listed problems and also why other changes may have been made in the PR if there are any.

So this sort of explanation is probably well suited for the explanation text in the comment below the heading. I’ll work on that at some point…

--- charjr:
>     1. **"what is the problem?"** - description of objective problem as you see it, or confirmed issue/adequately consensused proposal, should warn of the importance of the latter

How about:

```md
### What issue(s) does this solve?

Closes # 
```
I used the word _issue_ instead of _problem_ because it is the terminology used by Github. Might be a slight bit easier for those who's english is limited. Also to emphasise that the PR should be solving an already discussed issue.

Also by including a [Closing keyword](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/using-keywords-in-issues-and-pull-requests) contributers have to actively delete it first if it doesn't solve anything.

> 
>     3. **"did you really?"** - or did your computer do it for you, be honest

Throwing a spanner in, I'd maybe consider a checklist that mirrors the [contributer guidelines](https://contributing.godotengine.org/en/latest/engine/introduction.html#checklist-for-new-contributors) (where reasonable) right near the top to save time.

```md
## Contributer checklist
- [ ] I have performed a self-review of my code <!-- If not, set your PR as a draft until it's ready. --!>
- [ ] I have compiled and tested my code locally. <!-- If not, please set your PR as a draft until it's ready. --!>
- [ ] I have used AI to assist in this PR <!-- if yes, please tell us how --!>
```

Feel free to tweak it, or dismiss it entirely. But I feel like these three guidelines sum up the `"did you really?". The user has to proclaim that they self-reviewed and tested their code. If they didn't, well then, it doesn't meet the guidelines yet, so it should be a draft. 

A contributor blindly shovelling fresh heaps of LLM, if being honest, won't have self-reviewed. But then you ask, a final time, explicitly "Have you used AI?". If they lying through all of that... :shrug:.

```md
## Why use this approach?
```
+1 for ` ## Why use this approach?"`. It's simple and concise. It asks contributors if there are other methods, pros, cons, etc. They might just leave it short and sweet and link to a comment describing the agreed upon approach from the proposal etc.



--- allenwp:
> For one, pull requests that are small and trivial (e.g. quick bug fix) might get an **overly verbose** description, making it harder to understand the change at face value.

For this reason, I chose to limit the number of headings and provide headings that can be answered with a single word if they aren't valuable (heading number 3 and 4). My expectation is that contributors who are going to write an overly verbose description are already writing an overly verbose description, so this PR wouldn't change that behaviour in a substantial way. I might be entirely wrong, though. I really just don't know.

> Pull requests that are more complicated than the average (e.g. new feature) typically require an **even more verbose** description.

> Next, PRs might be **inadequately described** by the headings.

I see what you mean. Interestingly, I intentionally omitted a bunch of these things to mitigate the first problem of making PR descriptions overly verbose. My expectation is that authors of PRs that need or benefit from more explanation can and will this extra detail. And also that this PR won't make contributors describe less than they already are without any headings. Again, I might be entirely wrong. I don't have the ability to know, when it matters most, what behaviour change will happen in practice.

> I used the word _issue_ instead of _problem_

That's an interesting one. I chose the word "problem" because it aligns with the Godot contributing documentation. You're right that GitHub uses "issue", and both bug reports and proposals are tracked as "issues"... Hmmmm. One thing I've found when using this template with my PRs is that the word "problem" helps me think about my PR in terms of the logged issues on GitHub, but also other problems that have not been logged that my PR also solves. It seems quite often that my PRs both fix existing logged issues and also fix other problems at the same time. Hhhhhmmmmmmm... 🤔

Also, checklist might be a good thing to have, and also might be nice to have that suggestion to mark your PR as a draft if you're not finished.

Lots to think about :)

--- Ivorforce:
> Throwing a spanner in, I'd maybe consider a checklist that mirrors the [contributer guidelines](https://contributing.godotengine.org/en/latest/engine/introduction.html#checklist-for-new-contributors) (where reasonable) right near the top to save time.

Note that checkboxes show up as "tasks" in the GitHub UI - a fact that [has been critisized](https://github.com/godotengine/godot-proposals/issues/14616) for the proposal template already.

--- charjr:
> Note that checkboxes show up as "tasks" in the GitHub UI - a fact that [has been critisized](https://github.com/godotengine/godot-proposals/issues/14616) for the proposal template already.

That's a shame. It's not worth it if it's going to frustrate contributors.

> > I used the word _issue_ instead of _problem_
> 
> That's an interesting one. I chose the word "problem" because it aligns with the Godot contributing documentation.

That's a solid reason to stick to "problem" IMO. Godot's repository may be hosted on Github, but Godot's naming conventions take priority :balance_scale:.



--- allenwp:
Quite a few eyes (👀) have looked at this PR, but it is has no support (👍), so it's pretty clear to me that it has missed the mark.

I've opened a new PR that takes a different approach based on the feedback from this PR. Although it solves the same problems, it primarily uses comments to solve them instead of adding a bunch of headings, so I see it as a different paradigm and worthy of a separate new PR.

Closing as superseded by #118855

--- allenwp:
In this PR's discussion it was decided that it was better to not have a large number of headings and instead just have two headings (one for the problem and one for additional info). So the AI heading was omitted in the merged PR #118855.

Since then, #119894 has been opened to revisit the idea of an AI heading. There is also the similar #119242 that adds an AI heading. I'm mentioning these two new PRs in this discussion in case those subscribed are interested in continuing the discussion of adding this third heading to the PR template.

