clear;
clc;
clf;
%% ������
data = load('2022.10.14 16.04.21-zipf.mat'); % %
% data = load('2022.10.12 22.16.50-movie_tweet.mat'); %
% data = load('2022.10.11 21.28.03-movie_tweet.mat'); %
% data = load('2022.10.14 17.07.50-movie_comoda.mat'); %
% data = load('2022.10.14 16.39.41-movie_yahoo.mat'); %


% cache_hit_ratio
cache_hit_ratio_record_FIFO = data.cache_hit_ratio_record_FIFO;
cache_hit_ratio_record_LFU = data.cache_hit_ratio_record_LFU;
cache_hit_ratio_record_LRU = data.cache_hit_ratio_record_LRU;
cache_hit_ratio_record_TOC_S = data.cache_hit_ratio_record_TOC_S;
cache_hit_ratio_record_TOC_E = data.cache_hit_ratio_record_TOC_E;
cache_hit_ratio_record_DB = data.cache_hit_ratio_record_DB;
cache_hit_ratio_record_SB = data.cache_hit_ratio_record_SB;

cache_hit_ratio_record_TOC_S_transcode = data.cache_hit_ratio_record_TOC_S_transcode;
cache_hit_ratio_record_TOC_S_direct = data.cache_hit_ratio_record_TOC_S_direct;
cache_hit_ratio_record_TOC_E_transcode = data.cache_hit_ratio_record_TOC_E_transcode;
cache_hit_ratio_record_TOC_E_direct = data.cache_hit_ratio_record_TOC_E_direct;
cache_hit_ratio_record_LFU_transcode = data.cache_hit_ratio_record_LFU_transcode;
cache_hit_ratio_record_LFU_direct = data.cache_hit_ratio_record_LFU_direct;
cache_hit_ratio_record_LRU_transcode = data.cache_hit_ratio_record_LRU_transcode;
cache_hit_ratio_record_LRU_direct = data.cache_hit_ratio_record_LRU_direct;
cache_hit_ratio_record_FIFO_transcode = data.cache_hit_ratio_record_FIFO_transcode;
cache_hit_ratio_record_FIFO_direct = data.cache_hit_ratio_record_FIFO_direct;
cache_hit_ratio_record_DB_transcode = data.cache_hit_ratio_record_DB_transcode;
cache_hit_ratio_record_DB_direct = data.cache_hit_ratio_record_DB_direct;
cache_hit_ratio_record_SB_transcode = data.cache_hit_ratio_record_SB_transcode;
cache_hit_ratio_record_SB_direct = data.cache_hit_ratio_record_SB_direct;

utility_record_FIFO = data.utility_record_FIFO;
utility_record_LFU = data.utility_record_LFU;
utility_record_LRU = data.utility_record_LRU;
utility_record_TOC_S = data.utility_record_TOC_S;
utility_record_TOC_E = data.utility_record_TOC_E;
utility_record_DB = data.utility_record_DB;
utility_record_SB = data.utility_record_SB;

% 10�����ݵ��ƽ��ֵ��Ϊ��ͼ��
% 10�����ݵ�����ֵ����Сֵ����
cache_hit_ratio_record_FIFO_sampled = [];
cache_hit_ratio_record_LFU_sampled = [];
cache_hit_ratio_record_LRU_sampled = [];
cache_hit_ratio_record_TOC_S_sampled = [];

step_size = 100;
for i=1:step_size:length(cache_hit_ratio_record_FIFO)-mod(length(cache_hit_ratio_record_FIFO),step_size)
      cache_hit_ratio_record_FIFO_sampled=[cache_hit_ratio_record_FIFO_sampled,mean(cache_hit_ratio_record_FIFO(i:i+step_size-1))];
end
for i=1:step_size:length(cache_hit_ratio_record_LFU)-mod(length(cache_hit_ratio_record_LFU),step_size)
      cache_hit_ratio_record_LFU_sampled=[cache_hit_ratio_record_LFU_sampled,mean(cache_hit_ratio_record_LFU(i:i+step_size-1))];
end
for i=1:step_size:length(cache_hit_ratio_record_LRU)-mod(length(cache_hit_ratio_record_LRU),step_size)
      cache_hit_ratio_record_LRU_sampled=[cache_hit_ratio_record_LRU_sampled,mean(cache_hit_ratio_record_LRU(i:i+step_size-1))];
end
for i=1:step_size:length(cache_hit_ratio_record_TOC_S)-mod(length(cache_hit_ratio_record_TOC_S),step_size)
      cache_hit_ratio_record_TOC_S_sampled=[cache_hit_ratio_record_TOC_S_sampled,mean(cache_hit_ratio_record_TOC_S(i:i+step_size-1))];
end

cache_hit_ratio_record_FIFO_average = [];
cache_hit_ratio_record_LFU_average = [];
cache_hit_ratio_record_LRU_average = [];
cache_hit_ratio_record_TOC_S_average = [];
cache_hit_ratio_record_TOC_E_average = [];
cache_hit_ratio_record_DB_average = [];
cache_hit_ratio_record_SB_average = [];

for i=1:length(cache_hit_ratio_record_FIFO)
      cache_hit_ratio_record_FIFO_average(i)=mean(cache_hit_ratio_record_FIFO(1:i));
end
for i=1:length(cache_hit_ratio_record_LFU)
      cache_hit_ratio_record_LFU_average(i)=mean(cache_hit_ratio_record_LFU(1:i));
end
for i=1:length(cache_hit_ratio_record_LRU)
      cache_hit_ratio_record_LRU_average(i)=mean(cache_hit_ratio_record_LRU(1:i));
end
for i=1:length(cache_hit_ratio_record_TOC_S)
      cache_hit_ratio_record_TOC_S_average(i)=mean(cache_hit_ratio_record_TOC_S(1:i));
end
for i=1:length(cache_hit_ratio_record_TOC_E)
      cache_hit_ratio_record_TOC_E_average(i)=mean(cache_hit_ratio_record_TOC_E(1:i));
end
for i=1:length(cache_hit_ratio_record_DB)
      cache_hit_ratio_record_DB_average(i)=mean(cache_hit_ratio_record_DB(1:i));
end
for i=1:length(cache_hit_ratio_record_SB)
      cache_hit_ratio_record_SB_average(i)=mean(cache_hit_ratio_record_SB(1:i));
end




linewidth = 2;
hold on;
% plot((1:1:length(cache_hit_ratio_record_FIFO_sampled)),cache_hit_ratio_record_FIFO_sampled,'-.','LineWidth',linewidth);
% plot((1:1:length(cache_hit_ratio_record_LFU_sampled)),cache_hit_ratio_record_LFU_sampled,'-.','LineWidth',linewidth);
% plot((1:1:length(cache_hit_ratio_record_LRU_sampled)),cache_hit_ratio_record_LRU_sampled,'-.','LineWidth',linewidth);
% plot((1:1:length(cache_hit_ratio_record_TOC_S_sampled)),cache_hit_ratio_record_TOC_S_sampled,'-.','LineWidth',linewidth);

plot((1:1:length(cache_hit_ratio_record_FIFO_average)),cache_hit_ratio_record_FIFO_average,'-.','LineWidth',linewidth);
plot((1:1:length(cache_hit_ratio_record_LFU_average)),cache_hit_ratio_record_LFU_average,'-.','LineWidth',linewidth);
plot((1:1:length(cache_hit_ratio_record_LRU_average)),cache_hit_ratio_record_LRU_average,'-.','LineWidth',linewidth);
plot((1:1:length(cache_hit_ratio_record_TOC_S_average)),cache_hit_ratio_record_TOC_S_average,'-.','LineWidth',linewidth);
plot((1:1:length(cache_hit_ratio_record_TOC_E_average)),cache_hit_ratio_record_TOC_E_average,'-.','LineWidth',linewidth);
plot((1:1:length(cache_hit_ratio_record_DB_average)),cache_hit_ratio_record_DB_average,'-.','LineWidth',linewidth);
plot((1:1:length(cache_hit_ratio_record_SB_average)),cache_hit_ratio_record_SB_average,'-.','LineWidth',linewidth);


% cache_hit_ratio_TOC_S = sum(cache_hit_ratio_record_TOC_S)/length(cache_hit_ratio_record_TOC_S);
% cache_hit_ratio_LFU = sum(cache_hit_ratio_record_LFU)/length(cache_hit_ratio_record_LFU);
% cache_hit_ratio_LRU = sum(cache_hit_ratio_record_LRU)/length(cache_hit_ratio_record_LRU);
% cache_hit_ratio_FIFO = sum(cache_hit_ratio_record_FIFO)/length(cache_hit_ratio_record_FIFO);

%bar([cache_hit_ratio_FIFO,cache_hit_ratio_LFU,cache_hit_ratio_LRU,cache_hit_ratio_TOC_S])

legend('FIFO','LFU','LRU','TOC-S','TOC-E','DB','SB','Location','Best','fontsize',16,'NumColumns',4);


% h2=cdfplot(DP_reward);% ��matlab�л�ͼ����ʹ��cdfplot,�������
% line_width = 2.2;
% set(h1,'Linewidth',line_width,'LineStyle','-.');
% set(h2,'Linewidth',line_width,'LineStyle','-.');
% set(h3,'Linewidth',line_width,'LineStyle','-.');
% set(h4,'Linewidth',line_width,'LineStyle','-.');
% set(h5,'color',sixteen2ten('#ef5675')/255,'Linewidth',line_width,'LineStyle','-.');
% set(h6,'Linewidth',line_width,'LineStyle','-.');
% set(h7,'Linewidth',line_width,'LineStyle','-.');

% : - -. --
% set(h1,'color',sixteen2ten('#003f5c')/255,'Linewidth',line_width,'LineStyle','-.');
% set(h2,'color',sixteen2ten('#374c80')/255,'Linewidth',line_width,'LineStyle','-.');
% set(h3,'color',sixteen2ten('#7a5195')/255,'Linewidth',line_width,'LineStyle','-.');
% set(h4,'color',sixteen2ten('#bc5090')/255,'Linewidth',line_width,'LineStyle','-.');
% % set(h5,'color',sixteen2ten('#ef5675')/255,'Linewidth',line_width,'LineStyle','-.');
% set(h6,'color',sixteen2ten('#ff764a')/255,'Linewidth',line_width,'LineStyle','-.');
% set(h7,'color',sixteen2ten('#ffa600')/255,'Linewidth',line_width,'LineStyle','-.');
% set(h6,'color',sixteen2ten('#ffa600')/255,'Linewidth',3,'LineStyle','-');
set(gca,'box','on');
% set(gca,'xlim',[-25 20]);

title('');
xlabel('Time Slot');
ylabel('Cache Hit Ratio');

width = 800;
% height = 494.4;
height = 600;
set(gcf,'WindowStyle','normal');
set(gcf,'Position',[100,100,width,height]);
% set(gcf,'Position',[-1000,100,width,height]);
set(gca,'box','on'); % ͼ��߿�?
set(gca,'fontsize',22);
set(gca,'fontname','Times New Roman');
grid on;
set(gca,'GridLineStyle','-.','GridAlpha',0.05);
set(gca,'fontweight','bold');
set(gca,'linewidth',1.5);
% draw
coArray=['y','m','c','r','g','b','w','k'];%��ʼ��ɫ����
liArray=['o','x','+','*','-',':','-.','--','.'];%��ʼ��������
markerArray=['s','p','d','h','^','<'];%��ʼ��marker����


% set(gca,'xticklabel',[]); % xtick�ǿ̶ȣ�С���ߣ� xticklabel �̶�ֵ�������������ֵ��?
% set(gca,'yticklabel',[]); % xtick�ǿ̶ȣ�С���ߣ� xticklabel �̶�ֵ�������������ֵ��?
% set(gca,'ylim',[0 1.0]);



% plot(x,y,'-d','Color',[0.5 0.5 0.5],'LineWidth',3,'MarkerSize',8,'MarkerEdgeColor',[0.18 0.3 0.3]);
% hold on;
% 

% set(gca,'YColor',[0.2 0.2 0.2]);

% set(gca,'xlim',[0 60]);
% set(gca,'ylim',[0 15]);
% set(gca,'linewidth',3);
% set(gca,'fontweight','bold');


