

```dataviewjs
(async () => {
  const filePath = "02_Projects/Career/Grizzly Ridge/Epic/IDE.md"; // IDE 노트 경로
  const file = app.vault.getAbstractFileByPath(filePath);
  const content = await app.vault.read(file);

  // 정규식: "- [ ] 텍스트 ^ID" 매핑
  const matches = [...content.matchAll(/^- \[.\] (.*)\s\^([A-Za-z0-9-]+)$/gm)];

  const mapping = {};
  for (let m of matches) {
    const text = m[1]; // 할 일 텍스트
    const id = m[2];   // 블록 ID
    mapping[id] = text;
  }

  // 예시: 변수처럼 사용
  dv.paragraph(`GZRIDE1: ${mapping["GZRIDE1"]}`);
  dv.paragraph(`GZRIDE2: ${mapping["GZRIDE2"]}`);
  dv.paragraph(`20250421-073653: ${mapping["20250421-073653"]}`);

  // 전체 테이블 출력
  dv.table(["ID", "텍스트"], Object.entries(mapping));
})();
```