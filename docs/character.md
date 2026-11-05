# 邵艾伦 Q 版形象

- 本人视频：[《为什么我劝所有男人练薄肌？》](https://www.bilibili.com/video/BV1xa4k6vEpp/)
- 账号：邵艾伦Alan，B站 UID `4029133`。
- 参考来源：该视频公开封面，B站公开 view API 返回的作者、UID 与封面一致。
- [原封面](https://i2.hdslb.com/bfs/archive/15bb77d4eb2eb3387c7af6e481b29a82ea02ed3e.jpg)。参考照片仅用于本地创作参考，未放入仓库或安装包。
- [较早的账号头像](https://i1.hdslb.com/bfs/face/3b8af04c80ddd2bc246c19f9307cd6fc1025c684.jpg) 是金发、墨镜形象；本版选择视频封面的黑发、白 T、耳钉作为依据。
- 最终文件：`alan_water_pet/assets/alan-chibi-v1.png`。内置 imagegen 生成，真正的透明 alpha，非官方 Q 版插画，非真人照片。
- 形象生成与引用不意味着本人参与、授权或背书。

## 生成提示词

使用内置 imagegen，参考图为上述视频封面，`transparent_background=true`。

```text
Use case: stylized-concept, identity-preserving reference illustration. Asset type: one full-body desktop pet character sprite PNG with genuine transparent background. Input image 1 is a reference photo of Chinese content creator Shao Alan (邵艾伦), supplied from his own Bilibili video cover. Make a charming polished 2D chibi character recognizably based on the man in this photo: straight soft black fringe hair covering forehead, slim oval face and distinctive real facial proportions simplified (not generic random person), small silver hoop earring, fair skin, plain white short-sleeve T-shirt with NO text or logos, charcoal casual trousers, white sneakers. Large head about 45% total character height, slim adult body, warm gently assertive expression, three-quarter front view looking at viewer. One hand holding a big clear water jug with pale aqua water and mint green cap close to waist, other index finger slightly raised like explaining a point. Keep water jug visible and readable even when sprite is rendered 200px tall. Soft clean rounded outlines, subtle cel shading, muted green and warm neutral accents, professional indie desktop companion game asset, clean silhouette with a very subtle thin cream sticker outline around person and water bottle only. Single centered character, full body including shoes fully visible, tight useful framing with 5% transparent margin, vertical composition. NO background, NO rectangle, NO scene, NO frame, NO speech bubble, NO text, NO watermark, NO duplicated poses, NO extra characters. Preserve the identity features from the reference, do not reproduce cover typography. Genuine alpha transparency outside the character.
```
