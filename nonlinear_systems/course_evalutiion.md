Overall, I really enjoyed the course: it is fascinating subject area with tremedous insight into all things dynamic. We covered a lot of excellent material and the Dr. Jensen was was very clear as an instructor.

Most of my feedback on the course is rather technical in nature and pertains to the curriculum, which I assume was to some extent adapted from previous iterations of the course. The course was excellent as is, but at the highest level, here are two imprvovements that I would make:
2. Provide context into how nonlinear control fits into the overall landscape of control theory, and
3. Focus on practical, motivating examples throughout the course.

Detailed commentary can be found below.


** Instruction **
I think Dr. Jensen did a great job, especially considering it is the first time she has taught the course. Her lectures was engaging and had a knack for making abstract, difficult concepts seem concrete and intuitive.

** Overall Course Organization **

The content often felt a bit "in the weeds" of technical detail. I appreciate the focus on technical rigor, but would benefit from a presentation of the broader context. E.g. first half of course will discuss "system dynamics," second half "control methods". I.e. when beginning to discuss control methods, we missed an overview/taxonomy. E.g. breakdown by
2. Robust Control
3. Adaptive Control
4. Optimal Control
5. Constrained control
6. Geometric control

We really only covered Robust Control in detail. To focus on one particular area in detail is fine, but delineating how nonlinear control fits into the broader context of control theory would have been enriching.

** Integral Control **

I also wish the course had covered more Adaptive Control as well. Since my background is more classical controls oriented, I think it is a pity to omit connections between PID control and nonlinear control. The linear systems course was great in connecting the "Proportional" component by discussing concepts of feedback, state-space realizations, and pole placement. But it seems to me that integral control and adaptive control are closely intertwined. Given that PID control is the most ubiquitous control technology of the 21th century and remains highly relevant in industry today, I view the fact that integral control was not mentioned at all is a missed opportunity to bridge the gap between academia and industry. 

** Textbooks **

Overall:
2) The course's textbooks complemented each other well.
3) I have some minor qualms about Khalil's NonLinear Control: I think the aforementioned "in the weeds" comment on this course is inherited at least partially from this textbook.
4) I found that Slotine and Li's Applied Nonlinear Control was fantastic and covered many of Khalil's "blind spots".
5) I would consider Astom's Feedback Systems and Strogatz's Nonlinear Systems and Chaos as additional supplementary texts.




** Examples and Homework Sets **

Doing a better job tying together theory and application through detailed and realistic examples is one of the areas I think the course could most benefit from.  Emily gave a plethora of examples, which was very helpful in maintaining in-class engagement and making concepts more concrete. But the examples felt a bit repetitive at times. Repetition is certainly good to reinforce concepts, but at a certain point the rote algebraic manipulation felt not particularly practical (also see section on computation methods).

Perhaps, part of what made it feel _overly_ repetitive was the fact that a huge number of examples of dynamics consisted of a single class of functions, namely, polynomial/rational functions. Examples with trignometric functions, e.g., would have been nice. On the other hand, there were some of good examples of generalized classes of functions. E.g. proving stability properties of compositions g∘f (g: R->R, with |g|<=2) encompasses saturation functions which are encountered frequently in practice. While this generalization is nice, I think a more thorough discussion of specific common nonlinearities would be beneficial. Section 5.2 of Slotine is quite good. We covered saturations quite a bit, but I remain curious about the theory of hysteresis and deadzones, which I've seen/heard of commonly in practice ( within my personal robotics work, from a mentor of mine from the aerospace industry, within Power Systems literature, etc.).

At times, I found the examples and problem sets were a bit artificial and abstract. I thought the final two homework sets were some of the better ones (perhaps a bit of recency bias here); the earlier ones felt a bit mechanical and abstract, mirroring many of the in-class examples. The last assignment had two problems involving tangible, physical systems: the cart-pole and the jet turbine. I might design each assignment to include a few simpler, abstract problems to warm up the brain muscles, and then a couple more challenging/detailed/realistic problem. I also enjoyed the Dissipativity problem in the second to last assignment. I find problems which guide the student to creatively extend the material covered in lecture are particularly delightful and engaging. Spreading more problems like these earlier into the semester would make the problem sets more engaging and rewarding for future students.

Perks of a small class: it should hopefully allow course content to align examples given in class with the particular interests of the students. Dr. Dall'Anese made an effort to do so in his Online Optimization class last semester, and I thought this was great.

I also think an application or two relating to Power Systems would be appropriate, given that CU's ECEE department has a strength in that area.

The generality of control theory can be both a blessing and a curse. I believe an exceptional control program should be able to provide a broad set of well-developed and specific examples which help ground and inspire its theoretical insights.

** Computational Methods **
I thought the Sum of Squares methodology was one of the more interesting topics in the entire course. Perhaps it is only included as an optional topic at the end of the course since it is an area of relatively active research. To me, computational methods seem like an important practical tool towards the adoption of nonlinear control technologies.

SEJ

<!-- ** Control Group Institutional Structure **
Some vague thoughts on the Control group's place within ECEE:

To my surprise, the Controls and Power Systems focus areas within the ECEE department seem to be only loosely coupled from an institutional standpoint, while from a technical perspective they are intimately connected. I'm sure this perspective partly reflects my ignorance of university structure, but it seems to me that the controls group could benefit from closer collaborations with other focus areas/departments around CU and while the other focus aread would benefit from the control group's theoretical assets. -->


** Personal Background **
I wanted to provide some information on my background to place the succeeding comments into context. I took courses in 1) classical control theory and 2) nonlinear systems theory 3) various robotics (lab) classes as an undergraduate in Mechanical Engineering at UC Santa Barbara. Before starting my Master's at CU, I worked for 5 years at a robotics startup building a software platform to control industrial robotic manipulators in real-time for manufacturing applications. We employed a mixture of classical control techniques and optimization theory.

My motivation for this enrollment in the controls-focused traditional Master's program at CU Boulder is to solidify a mathematical theoretical foundation and to expand into new application areas, with a specific interest in Power Systems. 

With that said, here are my thoughts on the course:

I think Khalil is good in a reference/encyclopedic regard, but it's rather dense. I feel that it may miss the forest for the trees, sometimes.  Khalil's tome feels like a bit of a gatekeeper: "only those incredibly theoretically-inclined shall pass!" It's a fine line to tread between mathematical rigor and accessibility. As much as possible of both is ideal. I think overall the course struck a good balance.

As a specific example (disclaimer: this is more of an intuition than a well-researched idea), I used Strogatz's Nonlinear Dynamics and Chaos for the nonlinear dynamics course I took as an undergraduate. Strogatz (pg. 8) eliminates the distinction between autonomous and nonautonomous systems by simply adding time as a separate state variable. Maybe this is more justified from a "systems" perspective than a "control" perspective? But perhaps many of the theorems that Khalil proves independently for autonomous and non-autonomous systems can be viewed from a simpler, more unified perspective.

I don't know of any book that can replace Khalil in terms of comprehensiveness and rigor of the subject, but I would almost consider using it more as a supplementary text, and base the overall structure of the course around Slotine and Li's text. 

I found Applied Nonlinear Systems to be a fantastic textbook, full of compelling and detailed examples, while still maintaining a reasonable level of rigor. The conections between feedback linearization and differential geometry explored in section 6.2 fascinate me. At present, I can think of only one potential downside of this text: it is heavy biased towards robotic manipulators. This aligns well with my background, which likely explains why I find it so insightful, but perhaps for students coming from a different background it may be harder to follow.

I think that Astrom's Feedback Systems does a great job of elucidating connections between classical and modern control theory, as well as between industry and academia. It has a broad range of detailed examples that provide context motivation.(E.g. all of Ch. 3; I particularly relate to the example of noise cancelling headphones in Section 4.5). While it is a bit more geared towards linear controls, it has a number of sections on nonlinear systems which look quite good i.e. all of Ch. 4 and section 7.5. I think this would be useful as a supplementary text to both Linear and Nonlinear Control courses and help provide a sense of continuity between the two.

From my recollection (although it's been a while since I last gave a thorough read), it also has a good diversity of examples/applications. The style is informal which makes it relatively very approachable. It's of course more systems than controls oriented, but Parts I and II of the text could add a bit of color to the first half of the course. Part III on chaos is likely out of scope of this course, but the discussion of different types of bifurcations would nicely supplement the discussions early in the course around parameter sensitivities.