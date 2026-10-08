export function dynamic(text,sc,t){let m;
 if((m=text.match(/^([●○] )(.+)$/)))return m[1]+t(m[2]);
 if((m=text.match(/^(Open )?Image (\d*)(.*)$/)))return(m[1]?(sc?'打开':'開啟'):'')+(sc?'图片 ':'圖片 ')+m[2]+m[3];
 if((m=text.match(/^Version (\d+)$/)))return(sc?'版本 ':'版本 ')+m[1];
 if((m=text.match(/^Drawing · (\d+) of (\d+)$/)))return(sc?'绘制中':'繪圖中')+' · '+m[1]+'/'+m[2];
 if((m=text.match(/^(\d+) selected$/)))return(sc?'已选择 ':'已選取 ')+m[1];
 if((m=text.match(/^Waiting · (\d+) in line$/)))return(sc?'等待中 · 排在第 ':'等候中 · 排在第 ')+m[1]+(sc?' 位':' 位');
 if((m=text.match(/^Made (\d+) images?(?: in (\d+) s)? · Details$/)))return(sc?'已生成 ':'已產生 ')+m[1]+(sc?' 张图片':' 張圖片')+(m[2]?' · '+m[2]+' '+(sc?'秒':'秒'):'')+' · '+t('Details');
 if((m=text.match(/^(\d+) image\(s\) could not be completed\..*$/)))return m[1]+(sc?' 张图片未能完成。已完成的图片已保存，请重试。':' 張圖片未能完成。已完成的圖片已保留，請重試。');
 return null;
}
