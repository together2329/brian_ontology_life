## Plan

- [ ] 
- [ ]  
	- [ ] 
---
## Action

* 행동::  
	* 세부내용::
	* 리뷰::
	* 시작::  
	* 종료::  
	* 태그::  
	* 에너지::  
* 행동::  
	* 세부내용::
	* 리뷰::
	* 시작::  
	* 종료::  
	* 태그::  
	* 에너지::  
* 행동::  
	* 세부내용::
	* 리뷰::
	* 시작::  
	* 종료::  
	* 태그::  
	* 에너지::  
* 행동::  
	* 세부내용::
	* 리뷰::
	* 시작::  
	* 종료::  
	* 태그::  
	* 에너지::  
* 행동::  
	* 세부내용::
	* 리뷰::
	* 시작::  
	* 종료::  
	* 태그::  
	* 에너지::  
* 행동::  
	* 세부내용::
	* 리뷰::
	* 시작::  
	* 종료::  
	* 태그::  
	* 에너지::  
* 행동::  
	* 세부내용::
	* 리뷰::
	* 시작::  
	* 종료::  
	* 태그::  
	* 에너지::  
* 행동::  
	* 세부내용::
	* 리뷰::
	* 시작::  
	* 종료::  
	* 태그::  
	* 에너지::  
* 행동::  
	* 세부내용::
	* 리뷰::
	* 시작::  
	* 종료::  
	* 태그::  
	* 에너지::  
* 행동::  
	* 세부내용::
	* 리뷰::
	* 시작::  
	* 종료::  
	* 태그::  
	* 에너지::  
* 행동::  
	* 세부내용::
	* 리뷰::
	* 시작::  
	* 종료::  
	* 태그::  
	* 에너지::  
* 행동::  
	* 세부내용::
	* 리뷰::
	* 시작::  
	* 종료::  
	* 태그::  
	* 에너지::  

## Time Management

```dataviewjs
const items = dv.current().file.lists;

function extractFieldsAndDetails(children) {
    let detailsArr = [];
    let 리뷰 = "";
    let 시작 = "";
    let 종료 = "";
    let 태그 = "";
    let 에너지 = "";
    
    for (const child of children) {
        const txt = child.text.trim();
        if (txt.startsWith("리뷰::")) {
            리뷰 = txt.replace("리뷰::", "").trim();
        } else if (txt.startsWith("시작::")) {
            시작 = txt.replace("시작::", "").trim();
        } else if (txt.startsWith("종료::")) {
            종료 = txt.replace("종료::", "").trim();
        } else if (txt.startsWith("태그::")) {
            태그 = txt.replace("태그::", "").trim();
        } else if (txt.startsWith("에너지::")) {
            에너지 = txt.replace("에너지::", "").trim();
        } else if (txt.startsWith("세부내용::")) {
            const detailText = txt.replace("세부내용::", "").trim();
            if (detailText !== "") {
                detailsArr.push(detailText);
            }
        } else {
            if (txt !== "") {
                detailsArr.push(txt);
            }
        }
        if (child.children) {
            const subResult = extractFieldsAndDetails(child.children);
            if (subResult.세부내용 !== "") {
                detailsArr.push(subResult.세부내용);
            }
            if (!리뷰 && subResult.리뷰) {
                리뷰 = subResult.리뷰;
            }
            if (!시작 && subResult.시작) {
                시작 = subResult.시작;
            }
            if (!종료 && subResult.종료) {
                종료 = subResult.종료;
            }
            if (!태그 && subResult.태그) {
                태그 = subResult.태그;
            }
            if (!에너지 && subResult.에너지) {
                에너지 = subResult.에너지;
            }
        }
    }
    detailsArr = detailsArr.filter(text => text.length > 0);
    return {
        세부내용: detailsArr.join("<br>"),
        리뷰,
        시작,
        종료,
        태그,
        에너지
    };
}

const logEntries = items
    .filter(item => item.text && item.text.startsWith("행동::"))
    .map(item => {
        const 행동Text = item.text.replace("행동::", "").trim();
        let fields = { 세부내용: "", 리뷰: "", 시작: "", 종료: "", 태그: "", 에너지: "" };
        if (item.children) {
            fields = extractFieldsAndDetails(item.children);
        }
        // "행동", "세부내용", "리뷰" 열: 0.6em, min-width:150px
        const 행동 = `<div style="font-size:0.6em; min-width:150px;">${행동Text}</div>`;
        const 세부내용 = `<div style="font-size:0.6em; min-width:150px;">${fields.세부내용}</div>`;
        const 리뷰 = `<div style="font-size:0.6em; min-width:150px;">${fields.리뷰}</div>`;
        // "시작", "종료", "태그", "에너지" 열: 0.8em, max-width:100px
        const 시작 = `<div style="font-size:0.8em; max-width:100px;">${fields.시작}</div>`;
        const 종료 = `<div style="font-size:0.8em; max-width:100px;">${fields.종료}</div>`;
        const 태그 = `<div style="font-size:0.8em; max-width:100px;">${fields.태그}</div>`;
        const 에너지 = `<div style="font-size:0.8em; max-width:100px;">${fields.에너지}</div>`;
        return [행동, 세부내용, 리뷰, 시작, 종료, 태그, 에너지];
    });

// 헤더에도 동일하게 스타일 적용
const headers = [
    `<div style="font-size:0.6em; min-width:150px;">행동</div>`,
    `<div style="font-size:0.6em; min-width:150px;">세부내용</div>`,
    `<div style="font-size:0.6em; min-width:150px;">리뷰</div>`,
    `<div style="font-size:0.8em; max-width:100px;">시작</div>`,
    `<div style="font-size:0.8em; max-width:100px;">종료</div>`,
    `<div style="font-size:0.8em; max-width:100px;">태그</div>`,
    `<div style="font-size:0.8em; max-width:100px;">에너지</div>`
];

if (logEntries.length > 0) {
    dv.table(headers, logEntries);
} else {
    dv.paragraph("표시할 로그 항목이 없습니다.");
}
```

```query
line:GZRIDE
```

## Thinking 
## Review 
## Thank you 

