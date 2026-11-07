# Part 1 精简版（0–15s）— Gemini Omni 1.2 Flash

设置：时长 15s · 16:9 · 1080p · 按顺序上传 `part1_v2_refs/` 里的 6 张参考图（只有第 2 张换成了气球街景）。

改动（已按参考图 2 的实际构图修正开场描述）：删掉报纸梗；开场和气球梗合成一个连续跟拍镜头；剩下的梗每个 3 秒，分成"铺垫 → 围巾出手 → 反应"三拍。镜头从 7 个减到 5 个。

| 时间 | 镜头 |
|---|---|
| 0–4s | 开场跟拍 + 气球（一个镜头，不切） |
| 4–7s | 梯子 |
| 7–10s | 鸟蛋 |
| 10–13s | 茶杯 |
| 13–15s | 公园钩子：风筝挂树上，她解下围巾 |

## Prompt

```
A 15-second, 16:9, hand-drawn 2D storybook animation made of five shots joined by hard cuts, with relaxed, unhurried comic timing. This is part 1 of a two-part silent comedy short, "The Long Red Scarf".

Reference images:
- The first image is the character model sheet of the main character: a very tall, lanky young woman with a sleepy, half-lidded deadpan face, a short copper-orange bob with blunt bangs, freckles, a long charcoal-grey wool overcoat, black tights, brown lace-up boots, a paper bag with a baguette under her right arm, and an extremely long, chunky, bright red hand-knitted scarf with fringed ends. Keep her design exactly the same in every shot.
- The second image shows the balloon moment on the windy seaside hill-town street: she strolls to the right with her scarf streaming back, while behind her on the left a small boy in a yellow raincoat runs after his sky-blue balloon, which is floating up and away just above his reaching hand. It also sets the look of the whole film: dark-brown ink outlines, watercolor and gouache textures on paper grain, a soft hazy overcast palette of pale grey-teal, sage and ochre, autumn leaves in the air. Match this look in every shot.
- The third, fourth and fifth images show the compositions for the ladder shot, the bird's-nest shot and the café shot.
- The sixth image shows the final shot: a hilltop park with a yellow-and-blue kite tangled high in a bare tree and a little girl in a green coat pointing at it. The video ends on this composition.

Pacing: give every gag room to breathe. Each one has a clear setup, then one smooth move of the scarf, then a short reaction beat before the cut. Never rush or overlap the gags. She always moves from left to right and never turns back. Her face stays deadpan the whole time. Her scarf does all the helping, moving like a playful living thing, while she keeps strolling.

[0-4s] One continuous wide side-view shot with a slow tracking camera, no cuts, composed like the second image. She strolls left to right along the windy cobbled street, the long red scarf streaming back behind her, leaves swirling. Behind her, the small boy in the yellow raincoat runs after his sky-blue balloon as it floats up out of his reach; the balloon stays in frame. Without looking back, she gives a tiny flick of her head; the trailing tip of her scarf curls twice around the balloon string, pulls it down and places it back in the boy's hand. He stops, blinks at her, amazed, as she walks on.
[4-7s] Side shot by a pastel house, as in the third image. The window cleaner's wooden ladder starts to tip away from the wall while he flails. A beat later her scarf lashes out, loops around the ladder and the iron lamppost and gently pulls the ladder back upright. Still clinging on, he gives a shaky thumbs up as she strolls past.
[7-10s] Low angle under an autumn tree, as in the fourth image. Two blue eggs roll out of the nest and fall. Her scarf swings beneath them like a soft hammock, catches them, and tosses them gently back up into the nest, one after the other. The mother bird settles onto them, relieved.
[10-13s] Side shot outside a café with a striped awning, as in the fifth image. The waiter stumbles and his teapot and cups slide off the tray into the air. Her scarf slides underneath like a second tray, catches every piece without spilling a drop and tips them back onto his tray. He freezes mid-stumble on one leg, stunned.
[13-15s] Static wide shot of the hilltop park, as in the sixth image. She walks in and stops. The little girl in the green coat points up, close to tears, at the yellow-and-blue kite stuck high in the bare tree. She looks up at it, deadpan, and slowly unwinds the red scarf from her neck, holding it in both hands. Hold on this moment until the end.

Style: hand-drawn 2D storybook animation, fluid traditional character animation with clear comedic timing and smear frames on fast moves; the same ink line work, watercolor textures and colors in every shot; the red scarf is always the boldest color in the frame.

Audio: windy autumn ambience with one light, specific sound for each gag: a rubbery balloon squeak, a creaking wooden ladder, a soft woolly whoosh, two tiny taps of eggs, clinking china. The wind softens in the last shot. No music. No dialogue and no voices.

Do not use 3D, CGI or photorealism. Do not change her face, hair, coat or scarf between shots. Do not add a second scarf or change the scarf's color, length or texture. Do not show readable text, letters, signs, logos or subtitles. Do not add snow; it is still autumn. Do not let her turn around or walk from right to left. No camera shake.
```
