

```dataviewjs
// 🗓️ 날짜 범위 설정
const startDate = "2025-04-18"; // 시작 날짜 (YYYY-MM-DD)
const endDate = "2025-04-18";   // 종료 날짜 (YYYY-MM-DD)

// 날짜 범위 표시
dv.paragraph(`### ${startDate} ~ ${endDate} 활동 시간 분석`);

// 디버깅 모드 활성화
const DEBUG = true;

// 디버그 로깅 함수
function debug(...args) {
  if (DEBUG) {
    dv.paragraph(...args);
  }
}

// 날짜 범위 생성
function generateDateRange(start, end) {
  const dates = [];
  const currentDate = new Date(start);
  const lastDate = new Date(end);
  
  while (currentDate <= lastDate) {
    dates.push(currentDate.toISOString().split('T')[0]);
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return dates;
}

// 시간 포맷 함수
function formatDuration(totalMinutes) {
  if (totalMinutes === 0) return "0m";
  const minutes = Math.round(totalMinutes % 60);
  const hours = Math.floor(totalMinutes / 60);
  let result = "";
  if (hours > 0) result += `${hours}h`;
  if (minutes > 0) {
    if (hours > 0) result += " ";
    result += `${minutes}m`;
  }
  return result;
}

// 날짜 범위 생성
const dateRange = generateDateRange(startDate, endDate);

// 모든 날짜별 활동 데이터를 저장할 객체
const allActivities = {};
const dailyActivities = {};
const activityEnergies = {}; // 활동별 에너지 데이터 저장

// 에너지 태그 모니터링 카운터
let totalEnergyTagsFound = 0;
let successfulEnergyExtractions = 0;

// 각 날짜별로 활동 데이터 수집
for (const date of dateRange) {
  // 해당 날짜의 파일 가져오기
  const filePath = `01_Daily/Daily/${date}.md`;
  const page = dv.page(filePath);
  
  dailyActivities[date] = {};
  
  if (!page) {
    debug(`❌ ${date} 파일을 찾을 수 없습니다.`);
    continue;
  }
  
  // 파일 내용 가져오기
  const fileContent = await dv.io.load(page.file.path);
  debug(`${date} 파일 로드 완료, 길이: ${fileContent.length}`);
  
  // --- 섹션 추출 로직 ---
  const plannerHeaderText = "Day planner"; // 찾을 헤더 텍스트
  const headerRegex = new RegExp(`^#+\\s+${plannerHeaderText}\\s*$`, 'mi'); // 어떤 레벨이든 (# 개수 무관) 해당 텍스트를 가진 헤더를 찾는 정규식

  const headerMatch = fileContent.match(headerRegex); // 파일 내용에서 헤더 검색
  let sectionContent = "";

  if (headerMatch) {
    const headerStartIndex = headerMatch.index; // 찾은 헤더의 시작 위치
    const matchedHeader = headerMatch[0]; // 실제로 매치된 헤더 문자열 (예: "## Day planner")
    const contentAfterHeaderStart = fileContent.substring(headerStartIndex + matchedHeader.length); // 헤더 바로 다음 내용부터 추출

    // 다음 헤더를 찾아 섹션의 끝을 결정 (어떤 레벨이든 다음 헤더)
    const nextHeaderMatch = contentAfterHeaderStart.match(/^\s*#{1,}\s+/m);
    const contentEndIndex = nextHeaderMatch ? nextHeaderMatch.index : contentAfterHeaderStart.length; // 다음 헤더가 있으면 그 앞까지, 없으면 끝까지
    sectionContent = contentAfterHeaderStart.substring(0, contentEndIndex).trim(); // 섹션 내용 추출 및 공백 제거
    
    debug(`'Day planner' 섹션 추출됨, 길이: ${sectionContent.length}`);
  }
  // --- 섹션 추출 로직 끝 ---
  
  if (sectionContent) {
    const lines = sectionContent.split('\n');
    debug(`Day planner 라인 수: ${lines.length}`);
    
    // 개선된 정규식 - 더 다양한 시간 형식 처리
    // 개선된 정규식 - bold 형식(**13:00-15:00**)도 인식할 수 있도록 수정 
    // const lineRegex = /^\s*[-*]\s+(?:\*\*)?(\d{1,2}:\d{2})(?:\*\*)?\s*[-–]\s*(?:\*\*)?(\d{1,2}:\d{2})(?:\*\*)?\s*(.*?)(?:\s+#.*)?$/;

	// 시간 추출용 정규식
	const lineRegex = /^\s*[-*]\s+(?:\*\*)?(\d{1,2}:\d{2})(?:\*\*)?\s*[-–]\s*(?:\*\*)?(\d{1,2}:\d{2})(?:\*\*)?\s*(.*)$/;

	// 이모지 제거를 위한 대체 정규식 (단순 버전)
	const emojiRegex = /[\u{1F300}-\u{1FAFF}|\u{1F1E6}-\u{1F1FF}|\u{2600}-\u{26FF}|\u{2700}-\u{27BF}]/gu;

    for (const line of lines) {
      if (!line.trim() || line.trim().startsWith('#')) continue;

      const match = line.trim().match(lineRegex);
      if (match) {
        let startTimeStr = match[1];
        let endTimeStr = match[2];
        let activityName = match[3].trim();
        
        debug(`처리 중인 라인: "${line.trim()}"`);
        debug(`시간: ${startTimeStr}-${endTimeStr}, 활동명: "${activityName}"`);
        
        // 시간 형식 표준화 (한 자리 시간을 두 자리로)
        if (startTimeStr.length === 4) startTimeStr = "0" + startTimeStr;
        if (endTimeStr.length === 4) endTimeStr = "0" + endTimeStr;

        // --- 활동 이름 정리 개선 ---
        // 링크 및 태그 처리 (Unicode 지원하는 정규식으로 수정)
        const linkMatches = activityName.match(/!?\[\[(.*?)\]\]/g) || [];
        
        // 수정된 태그 정규식 (한글 포함 유니코드 문자 지원)
        //const tagMatches = activityName.match(/#[\p{L}\p{N}_]+/gu) || [];

	    // 태그 추출
	    const tagMatches = [...activityName.matchAll(/\B#([\p{L}\p{N}_]+)/gu)].map(m => `#${m[1]}`);

	    // 활동명 정리: 태그 제거, 이모지 제거, 공백 정리
		const cleanActivityName = activityName
			  .replace(/#[^\s#]+/g, '')     // 태그 제거 (한글, 영문 포함)
			  .replace(emojiRegex, '')      // 이모지 제거
			  .replace(/\s+/g, ' ')         // 여러 공백 -> 하나로
			  .trim();                      // 양 끝 공백 제거

		activityName = cleanActivityName;

        debug(`찾은 태그(${tagMatches.length}개):`, tagMatches);
        
        // 링크와 기본 텍스트 분리 처리
        let mainText = activityName;
        for (const link of linkMatches) {
          mainText = mainText.replace(link, '');
        }
        
        // 태그는 별도 저장하고 본문에서 제거
        //let tags = "";
        //for (const tag of tagMatches) {
        //  mainText = mainText.replace(tag, '');
       //   tags += tag + " ";
        //}
        
        // 정리
        mainText = mainText.replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '');
        mainText = mainText.replace(/^[ *_~]+|[ *_~]+$/g, '');
        mainText = mainText.replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, '$1').trim();
        
        // 링크가 있으면 본문에 추가
        if (linkMatches.length > 0) {
          mainText = mainText + " " + linkMatches.join(" ");
        }
        
        // 최종 정리된 활동명
        activityName = (mainText || "(설명 없음)").trim();
        
        // 에너지 태그가 있으면 활동명에 추가하고 에너지 값 저장
        const energyTag = tagMatches.find(tag => tag.startsWith('#에너지'));
        let energyLevel = 0;
        if (energyTag) {
          totalEnergyTagsFound++;
          //activityName += ` (${energyTag})`;
          // 에너지 값 추출 (#에너지50 -> 50)
          const energyMatch = energyTag.match(/#에너지(\d+)/u);
          debug(`에너지 태그 매치 결과:`, energyMatch);
          
          if (energyMatch && energyMatch[1]) {
            energyLevel = parseInt(energyMatch[1]);
            successfulEnergyExtractions++;
            debug(`에너지 태그 발견: ${energyTag}, 추출된 레벨: ${energyLevel}`);
          } else {
            debug(`⚠️ 에너지 값 추출 실패: ${energyTag}`);
          }
        }
        // --- 활동 이름 정리 끝 ---
        
        try {
          const start = new Date(`${date}T${startTimeStr}:00`);
          const end = new Date(`${date}T${endTimeStr}:00`);

          if (isNaN(start.getTime()) || isNaN(end.getTime())) {
            debug(`⚠️ 유효하지 않은 시간 포맷 건너뜀: ${line.trim()}`);
            continue;
          }
          
          // 시간 순서 확인 및 날짜 경계 처리
          let adjustedEnd = end;
          if (start >= end) {
            // 날짜를 넘어가는 케이스 처리 (예: 23:00-01:00)
            if (startTimeStr.startsWith("2") && endTimeStr.startsWith("0")) {
              adjustedEnd = new Date(`${date}T${endTimeStr}:00`);
              adjustedEnd.setDate(adjustedEnd.getDate() + 1);
            } else {
              debug(`⚠️ 종료 시간이 시작 시간보다 빠르거나 같은 항목 건너뜀: ${line.trim()}`);
              continue;
            }
          }

          const duration = (adjustedEnd - start) / (1000 * 60); // 분 단위
          
          if (duration > 0) {
            // 해당 날짜의 활동 정보 저장
            dailyActivities[date][activityName] = (dailyActivities[date][activityName] || 0) + duration;
            
            // 전체 활동 목록에 추가
            if (!allActivities[activityName]) {
              allActivities[activityName] = {};
            }
            allActivities[activityName][date] = (allActivities[activityName][date] || 0) + duration;
            
            // 에너지 데이터 저장
            if (energyLevel > 0) {
              debug(`에너지 레벨 ${energyLevel}이 추가됨: ${activityName}, 길이: ${duration}분`);
              
              if (!activityEnergies[activityName]) {
                activityEnergies[activityName] = {
                  totalEnergy: 0,
                  totalDuration: 0,
                  dateCounts: {}
                };
              }
              
              if (!activityEnergies[activityName].dateCounts[date]) {
                activityEnergies[activityName].dateCounts[date] = {
                  energySum: 0,
                  durationSum: 0
                };
              }
              
              // 날짜별 에너지-시간 누적
              activityEnergies[activityName].dateCounts[date].energySum += energyLevel * duration;
              activityEnergies[activityName].dateCounts[date].durationSum += duration;
              
              // 전체 에너지-시간 누적
              activityEnergies[activityName].totalEnergy += energyLevel * duration;
              activityEnergies[activityName].totalDuration += duration;
              
              debug(`${activityName}의 누적 에너지: ${activityEnergies[activityName].totalEnergy}, 누적 시간: ${activityEnergies[activityName].totalDuration}`);
            } else {
              debug(`⚠️ 에너지 레벨 0 또는 미설정: ${activityName}`);
            }
          }
        } catch (e) {
          debug(`❌ 시간 처리 오류: ${line.trim()}`, e);
          dv.span(`❌ 시간 처리 오류 발생: ${line.trim()}. 개발자 콘솔(Ctrl+Shift+I) 확인`);
        }
      } else if (line.trim()) {
        // 매치되지 않은 라인 로깅 (디버깅용)
        debug(`매치되지 않은 라인: "${line.trim()}"`);
      }
    }
  } else {
    debug(`ℹ️ ${date}: 'Day planner' 섹션을 찾을 수 없거나 내용이 없습니다.`);
  }
}

// 에너지 데이터 현황 로깅
debug("===== 에너지 데이터 현황 =====");
debug(`총 발견된 에너지 태그: ${totalEnergyTagsFound}`);
debug(`성공적으로 추출된 에너지 값: ${successfulEnergyExtractions}`);
debug("활동별 에너지 데이터:", activityEnergies);

// 모든 활동 목록 가져오기
const allActivityNames = Object.keys(allActivities);
debug(`총 활동 수: ${allActivityNames.length}`);

// 테이블 헤더 생성 
let headers = ["활동"];
for (const date of dateRange) {
  // 날짜 포맷 변경 (YYYY-MM-DD -> MM/DD)
  const shortDate = date.substring(5).replace("-", "/");
  headers.push(shortDate);
}
headers.push("합계");
headers.push("비율");
headers.push("평균 에너지");

// 테이블 데이터 생성
const tableData = [];

// 총 기록 시간 계산
let totalAllActivitiesTime = 0;
for (const activity of allActivityNames) {
  for (const date of dateRange) {
    totalAllActivitiesTime += allActivities[activity][date] || 0;
  }
}

// 각 활동별로 날짜별 시간 및 합계, 퍼센트, 평균 에너지 계산
for (const activity of allActivityNames) {
  const row = [activity];
  let totalMinutes = 0;
  
  for (const date of dateRange) {
    const minutes = allActivities[activity][date] || 0;
    row.push(minutes > 0 ? formatDuration(minutes) : "-");
    totalMinutes += minutes;
  }
  
  // 합계 시간
  row.push(formatDuration(totalMinutes));
  
  // 퍼센트 계산
  const percentage = Math.round((totalMinutes / totalAllActivitiesTime) * 100);
  row.push(`${percentage}%`);
  
  // 평균 에너지 계산
  let avgEnergy = "-";
  if (activityEnergies[activity] && activityEnergies[activity].totalDuration > 0) {
    const energyAvg = Math.round(activityEnergies[activity].totalEnergy / activityEnergies[activity].totalDuration);
    debug(`${activity}의 평균 에너지 계산: ${activityEnergies[activity].totalEnergy} / ${activityEnergies[activity].totalDuration} = ${energyAvg}`);
    avgEnergy = `${energyAvg}`;
  } else {
    debug(`${activity}에 에너지 데이터 없음`);
  }
  row.push(avgEnergy);
  
  tableData.push(row);
}

// 테이블 데이터 정렬 (합계 시간 기준 내림차순)
tableData.sort((a, b) => {
  const getMinutes = (timeStr) => {
    if (timeStr === "-" || timeStr === "0m") return 0;
    let totalMinutes = 0;
    const hourMatch = timeStr.match(/(\d+)h/);
    const minuteMatch = timeStr.match(/(\d+)m/);
    if (hourMatch) totalMinutes += parseInt(hourMatch[1]) * 60;
    if (minuteMatch) totalMinutes += parseInt(minuteMatch[1]);
    return totalMinutes;
  };
  
  const totalColumnIndex = headers.indexOf("합계");
  if (totalColumnIndex !== -1) {
    return getMinutes(b[totalColumnIndex]) - getMinutes(a[totalColumnIndex]);
  }
  return 0;
});

// 테이블 형식 생성
let table = `| ${headers.join(" | ")} |\n`;
table += `| ${headers.map(_ => "---").join(" | ")} |\n`;

for (const row of tableData) {
  table += `| ${row.join(" | ")} |\n`;
}

// 테이블 출력
dv.paragraph(table);

// 에너지 평균 계산
let totalEnergyWeighted = 0;
let totalEnergyDuration = 0;

for (const activity in activityEnergies) {
  debug(`활동: ${activity}, 에너지: ${activityEnergies[activity].totalEnergy}, 시간: ${activityEnergies[activity].totalDuration}`);
  totalEnergyWeighted += activityEnergies[activity].totalEnergy;
  totalEnergyDuration += activityEnergies[activity].totalDuration;
}

const overallAvgEnergy = totalEnergyDuration > 0 ? 
  Math.round(totalEnergyWeighted / totalEnergyDuration) : 0;

dv.paragraph(`**총 기록 시간:** ${formatDuration(totalAllActivitiesTime)} | **전체 평균 에너지:** ${overallAvgEnergy}`);

// 디버깅 정보 출력
if (DEBUG) {
  dv.paragraph("### 디버깅 정보");
  dv.paragraph(`- 총 발견된 에너지 태그: ${totalEnergyTagsFound}`);
  dv.paragraph(`- 성공적으로 추출된 에너지 값: ${successfulEnergyExtractions}`);
  dv.paragraph(`- 에너지 데이터가 있는 활동 수: ${Object.keys(activityEnergies).length}`);
  dv.paragraph(`- 모든 활동 수: ${allActivityNames.length}`);
  dv.paragraph("자세한 정보는 개발자 콘솔(Ctrl+Shift+I)에서 확인하세요.");
}
```

