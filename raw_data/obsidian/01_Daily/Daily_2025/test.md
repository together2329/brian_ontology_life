```python
dataviewjs
// 분석할 날짜 범위 설정
const startDate = "2025-04-16";
const endDate = "2025-04-18";

// 날짜 배열 생성 함수
function getDateRange(start, end) {
  const dates = [];
  let current = new Date(start);
  const last = new Date(end);

  while (current <= last) {
    dates.push(current.toISOString().slice(0, 10)); // YYYY-MM-DD
    current.setDate(current.getDate() + 1);
  }

  return dates;
}

const dates = getDateRange(startDate, endDate);
const filePaths = dates.map(date => `01_Daily/Daily/${date}.md`);

const allActivities = {}; // { 활동: {날짜: duration, ...}, ... }

for (let i = 0; i < dates.length; i++) {
  const date = dates[i];
  const filePath = filePaths[i];
  const page = dv.page(filePath);
  if (!page) continue;

  const fileContent = await dv.io.load(page.file.path);
  const plannerHeader = "## Day planner";
  const headerStartIndex = fileContent.toLowerCase().indexOf(plannerHeader.toLowerCase());
  if (headerStartIndex === -1) continue;

  const contentAfterHeader = fileContent.substring(headerStartIndex + plannerHeader.length);
  const nextHeaderMatch = contentAfterHeader.match(/^\s*#{2,}\s+/m);
  const contentEndIndex = nextHeaderMatch ? nextHeaderMatch.index : contentAfterHeader.length;
  const sectionContent = contentAfterHeader.substring(0, contentEndIndex).trim();
  if (!sectionContent) continue;

  const lines = sectionContent.split("\n");
  const lineRegex = /^\s*[-*]\s+(?:\*\*?)?(\d{2}:\d{2})\s*[-–]\s*(\d{2}:\d{2})(?:\*\*?)?\s*(.*?)(?:\s+#.*)?$/;

  for (const line of lines) {
    if (line.trim().startsWith("#")) continue;

    const match = line.trim().match(lineRegex);
    if (match) {
      const startTimeStr = match[1];
      const endTimeStr = match[2];
      let activityName = match[3].trim();

      // 링크 보존
      const linkMatch = activityName.match(/!?(\[\[.*?\]\])/);
      const preservedLink = linkMatch ? linkMatch[1] : null;

      // 클린업
      activityName = activityName.replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '');
      activityName = activityName.replace(/^[ *_~]+|[ *_~]+$/g, '');
      activityName = activityName.replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, "$1").trim();
      if (preservedLink) activityName = preservedLink;
      if (!activityName) activityName = "(설명 없음)";

      try {
        const start = new Date(`${date}T${startTimeStr}:00`);
        const end = new Date(`${date}T${endTimeStr}:00`);
        if (isNaN(start.getTime()) || isNaN(end.getTime())) continue;
        if (start >= end) continue;

        const duration = (end - start) / (1000 * 60); // 분
        if (!allActivities[activityName]) {
          allActivities[activityName] = {};
        }
        allActivities[activityName][date] = (allActivities[activityName][date] || 0) + duration;
      } catch (e) {
        console.error(`시간 파싱 오류: ${line.trim()}`, e);
      }
    }
  }
}

// 형식 함수
function formatDuration(mins) {
  if (!mins || mins === 0) return "";
  const h = Math.floor(mins / 60);
  const m = Math.round(mins % 60);
  return `${h > 0 ? `${h}h` : ""}${h > 0 && m > 0 ? " " : ""}${m > 0 ? `${m}m` : ""}`;
}

// 테이블 헤더
const headers = ["Activity", ...dates, "Total"];

// 테이블 데이터 정리
const tableRows = Object.entries(allActivities).map(([activity, durations]) => {
  const row = [activity]; // 링크 그대로 문자열로 유지
  let total = 0;

  for (const date of dates) {
    const mins = durations[date] || 0;
    row.push(formatDuration(mins));
    total += mins;
  }
  row.push(formatDuration(total));
  return row;
});

// 정렬 (총합 기준)
tableRows.sort((a, b) => {
  const toMinutes = str => {
    const match = str.match(/(?:(\d+)h)?\s*(?:(\d+)m)?/);
    const hours = match?.[1] ? parseInt(match[1]) : 0;
    const mins = match?.[2] ? parseInt(match[2]) : 0;
    return hours * 60 + mins;
  };
  return toMinutes(b[b.length - 1]) - toMinutes(a[a.length - 1]);
});

// 마크다운 테이블 문자열로 만들기
function makeMarkdownTable(headers, rows) {
  const allRows = [headers, headers.map(() => "---"), ...rows];
  return allRows.map(r => `| ${r.join(" | ")} |`).join("\n");
}

// 테이블 출력
dv.paragraph(makeMarkdownTable(headers, tableRows));
```


```dataviewjs
// 분석할 날짜 범위 설정
const startDate = "2025-04-16";
const endDate = "2025-04-18";

// 날짜 배열 생성 함수
function getDateRange(start, end) {
  const dates = [];
  let current = new Date(start);
  const last = new Date(end);

  while (current <= last) {
    dates.push(current.toISOString().slice(0, 10));
    current.setDate(current.getDate() + 1);
  }

  return dates;
}

const dates = getDateRange(startDate, endDate);
const filePaths = dates.map(date => `01_Daily/Daily/${date}.md`);

const allActivities = {};

for (let i = 0; i < dates.length; i++) {
  const date = dates[i];
  const filePath = filePaths[i];
  const page = dv.page(filePath);
  if (!page) continue;

  const fileContent = await dv.io.load(page.file.path);
  const plannerHeader = "## Day planner";
  const headerStartIndex = fileContent.toLowerCase().indexOf(plannerHeader.toLowerCase());
  if (headerStartIndex === -1) continue;

  const contentAfterHeader = fileContent.substring(headerStartIndex + plannerHeader.length);
  const nextHeaderMatch = contentAfterHeader.match(/^\s*#{2,}\s+/m);
  const contentEndIndex = nextHeaderMatch ? nextHeaderMatch.index : contentAfterHeader.length;
  const sectionContent = contentAfterHeader.substring(0, contentEndIndex).trim();
  if (!sectionContent) continue;

  const lines = sectionContent.split("\n");
  const lineRegex = /^\s*[-*]\s+(?:\*\*?)?(\d{2}:\d{2})\s*[-–]\s*(\d{2}:\d{2})(?:\*\*?)?\s*(.*?)(?:\s+#.*)?$/;

  for (const line of lines) {
    if (line.trim().startsWith("#")) continue;

    const match = line.trim().match(lineRegex);
    if (match) {
      const startTimeStr = match[1];
      const endTimeStr = match[2];
      let activityName = match[3].trim();

      // 링크 보존
      const linkMatch = activityName.match(/!?(\[\[.*?\]\])/);
      const preservedLink = linkMatch ? linkMatch[1] : null;

      // 이모지 및 꾸밈 제거
      activityName = activityName.replace(/^[^\p{L}\p{N}\[]/, ''); // 이모지 제거 (앞부분 한 글자)
      activityName = activityName.replace(/^[ *_~]+|[ *_~]+$/g, '');
      activityName = activityName.replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, "$1").trim();

      // 링크 보존
      if (preservedLink) activityName = preservedLink;
      if (!activityName) activityName = "(설명 없음)";

      try {
        const start = new Date(`${date}T${startTimeStr}:00`);
        const end = new Date(`${date}T${endTimeStr}:00`);
        if (isNaN(start.getTime()) || isNaN(end.getTime())) continue;
        if (start >= end) continue;

        const duration = (end - start) / (1000 * 60);
        if (!allActivities[activityName]) {
          allActivities[activityName] = {};
        }
        allActivities[activityName][date] = (allActivities[activityName][date] || 0) + duration;
      } catch (e) {
        console.error(`시간 파싱 오류: ${line.trim()}`, e);
      }
    }
  }
}

// 시간 포맷 함수
function formatDuration(mins) {
  if (!mins || mins === 0) return "";
  const h = Math.floor(mins / 60);
  const m = Math.round(mins % 60);
  return `${h > 0 ? `${h}h` : ""}${h > 0 && m > 0 ? " " : ""}${m > 0 ? `${m}m` : ""}`;
}

// 테이블 헤더
const headers = ["Activity", ...dates, "Total"];

// 테이블 내용 구성
const tableRows = Object.entries(allActivities).map(([activity, durations]) => {
  const row = [activity];
  let total = 0;

  for (const date of dates) {
    const mins = durations[date] || 0;
    row.push(formatDuration(mins));
    total += mins;
  }

  row.push(formatDuration(total));
  return row;
});

// 총합 기준으로 정렬
tableRows.sort((a, b) => {
  const toMinutes = str => {
    const match = str.match(/(?:(\d+)h)?\s*(?:(\d+)m)?/);
    const hours = match?.[1] ? parseInt(match[1]) : 0;
    const mins = match?.[2] ? parseInt(match[2]) : 0;
    return hours * 60 + mins;
  };
  return toMinutes(b[b.length - 1]) - toMinutes(a[a.length - 1]);
});

// 마크다운 테이블 생성 함수
function makeMarkdownTable(headers, rows) {
  const allRows = [headers, headers.map(() => "---"), ...rows];
  return allRows.map(r => `| ${r.join(" | ")} |`).join("\n");
}

// 출력
dv.paragraph(makeMarkdownTable(headers, tableRows));
```