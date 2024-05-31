library(ggplot2)
setwd('~/Desktop/YMAlab/zhangtools/CAME_test/_temp')

#DATA ACQUISITION
##resolution
###### 

norm1 <- read.table('norm1/train_logs.csv',sep=",",header=T) #--take the output of backtrack.py
norm2 <- read.table('norm2/train_logs.csv',sep=",",header=T)
norm3 <- read.table('norm3/train_logs.csv',sep=",",header=T)
norm4 <- read.table('norm4/train_logs.csv',sep=",",header=T)
norm5 <- read.table('norm5/train_logs.csv',sep=",",header=T)

r1<-read.table('norm_reso0.1_1/train_logs.csv',sep=",",header=T)
r2<-read.table('norm_reso0.1_2/train_logs.csv',sep=",",header=T)
r3<-read.table('norm_reso0.1_3/train_logs.csv',sep=",",header=T)
r4<-read.table('norm_reso0.1_4/train_logs.csv',sep=",",header=T)
r5<-read.table('norm_reso0.1_5/train_logs.csv',sep=",",header=T)

re1<-read.table('norm_reso0.2_1/train_logs.csv',sep=",",header=T)
re2<-read.table('norm_reso0.2_2/train_logs.csv',sep=",",header=T)
re3<-read.table('norm_reso0.2_3/train_logs.csv',sep=",",header=T)
re4<-read.table('norm_reso0.2_4/train_logs.csv',sep=",",header=T)
re5<-read.table('norm_reso0.2_5/train_logs.csv',sep=",",header=T)

res1<-read.table('norm_reso0.3_1/train_logs.csv',sep=",",header=T)
res2<-read.table('norm_reso0.3_2/train_logs.csv',sep=",",header=T)
res3<-read.table('norm_reso0.3_3/train_logs.csv',sep=",",header=T)
res4<-read.table('norm_reso0.3_4/train_logs.csv',sep=",",header=T)
res5<-read.table('norm_reso0.3_5/train_logs.csv',sep=",",header=T)

reso1<-read.table('norm_reso0.5_1/train_logs.csv',sep=",",header=T)
reso2<-read.table('norm_reso0.5_2/train_logs.csv',sep=",",header=T)
reso3<-read.table('norm_reso0.5_3/train_logs.csv',sep=",",header=T)
reso4<-read.table('norm_reso0.5_4/train_logs.csv',sep=",",header=T)
reso5<-read.table('norm_reso0.5_5/train_logs.csv',sep=",",header=T)

resol1<-read.table('norm_reso0.6_1/train_logs.csv',sep=",",header=T)
resol2<-read.table('norm_reso0.6_2/train_logs.csv',sep=",",header=T)
resol3<-read.table('norm_reso0.6_3/train_logs.csv',sep=",",header=T)
resol4<-read.table('norm_reso0.6_4/train_logs.csv',sep=",",header=T)
resol5<-read.table('norm_reso0.6_5/train_logs.csv',sep=",",header=T)

resolu1<-read.table('norm_reso0.7_1/train_logs.csv',sep=",",header=T)
resolu2<-read.table('norm_reso0.7_2/train_logs.csv',sep=",",header=T)
resolu3<-read.table('norm_reso0.7_3/train_logs.csv',sep=",",header=T)
resolu4<-read.table('norm_reso0.7_4/train_logs.csv',sep=",",header=T)
resolu5<-read.table('norm_reso0.7_5/train_logs.csv',sep=",",header=T)

resolut1<-read.table('norm_reso0.8_1/train_logs.csv',sep=",",header=T)
resolut2<-read.table('norm_reso0.8_2/train_logs.csv',sep=",",header=T)
resolut3<-read.table('norm_reso0.8_3/train_logs.csv',sep=",",header=T)
resolut4<-read.table('norm_reso0.8_4/train_logs.csv',sep=",",header=T)
resolut5<-read.table('norm_reso0.8_5/train_logs.csv',sep=",",header=T)

resoluti1<-read.table('norm_reso0.9_1/train_logs.csv',sep=",",header=T)
resoluti2<-read.table('norm_reso0.9_2/train_logs.csv',sep=",",header=T)
resoluti3<-read.table('norm_reso0.9_3/train_logs.csv',sep=",",header=T)
resoluti4<-read.table('norm_reso0.9_4/train_logs.csv',sep=",",header=T)
resoluti5<-read.table('norm_reso0.9_5/train_logs.csv',sep=",",header=T)
#####

n1 <- read.table('n_oo_n_oo_loop1/train_logs.csv',sep=",",header=T) #--take the output of backtrack.py
n2<- read.table('n_oo_n_oo_loop2/train_logs.csv',sep=",",header=T) 
n3<- read.table('n_oo_n_oo_loop3/train_logs.csv',sep=",",header=T) 
n4<- read.table('n_oo_n_oo_loop4/train_logs.csv',sep=",",header=T) 
n5<- read.table('n_oo_n_oo_loop5/train_logs.csv',sep=",",header=T) 

oo1<-read.table('n_oo_loop1/train_logs.csv',sep=",",header=T)
oo2<-read.table('n_oo_loop2/train_logs.csv',sep=",",header=T)
oo3<-read.table('n_oo_loop3/train_logs.csv',sep=",",header=T)
oo4<-read.table('n_oo_loop4/train_logs.csv',sep=",",header=T)
oo5<-read.table('n_oo_loop5/train_logs.csv',sep=",",header=T)

ov1<-read.table('n_oo_loop_n_vv_loop1/train_logs.csv',sep=",",header=T)
ov2<-read.table('n_oo_loop_n_vv_loop2/train_logs.csv',sep=",",header=T)
ov3<-read.table('n_oo_loop_n_vv_loop3/train_logs.csv',sep=",",header=T)
ov4<-read.table('n_oo_loop_n_vv_loop4/train_logs.csv',sep=",",header=T)
ov5<-read.table('n_oo_loop_n_vv_loop5/train_logs.csv',sep=",",header=T)

no1<-read.table('n_oo1/train_logs.csv',sep=",",header=T)
no2<-read.table('n_oo2/train_logs.csv',sep=",",header=T)
no3<-read.table('n_oo3/train_logs.csv',sep=",",header=T)
no4<-read.table('n_oo4/train_logs.csv',sep=",",header=T)
no5<-read.table('n_oo5/train_logs.csv',sep=",",header=T)

nv1<-read.table('n_vv_loop1/train_logs.csv',sep=",",header=T)
nv2<-read.table('n_vv_loop2/train_logs.csv',sep=",",header=T)
nv3<-read.table('n_vv_loop3/train_logs.csv',sep=",",header=T)
nv4<-read.table('n_vv_loop4/train_logs.csv',sep=",",header=T)
nv5<-read.table('n_vv_loop5/train_logs.csv',sep=",",header=T)


#####
r1<-read.table('norm_clusReso0.1_1/train_logs.csv',sep=",",header=T)
r2<-read.table('norm_clusReso0.1_2/train_logs.csv',sep=",",header=T)
r3<-read.table('norm_clusReso0.1_3/train_logs.csv',sep=",",header=T)
r4<-read.table('norm_clusReso0.1_4/train_logs.csv',sep=",",header=T)
r5<-read.table('norm_clusReso0.1_5/train_logs.csv',sep=",",header=T)

re1<-read.table('norm_clusReso0.2_1/train_logs.csv',sep=",",header=T)
re2<-read.table('norm_clusReso0.2_2/train_logs.csv',sep=",",header=T)
re3<-read.table('norm_clusReso0.2_3/train_logs.csv',sep=",",header=T)
re4<-read.table('norm_clusReso0.2_4/train_logs.csv',sep=",",header=T)
re5<-read.table('norm_clusReso0.2_5/train_logs.csv',sep=",",header=T)

res1<-read.table('norm_clusReso0.3_1/train_logs.csv',sep=",",header=T)
res2<-read.table('norm_clusReso0.3_2/train_logs.csv',sep=",",header=T)
res3<-read.table('norm_clusReso0.3_3/train_logs.csv',sep=",",header=T)
res4<-read.table('norm_clusReso0.3_4/train_logs.csv',sep=",",header=T)
res5<-read.table('norm_clusReso0.3_5/train_logs.csv',sep=",",header=T)

norm1<-read.table('norm_clusReso0.4_1/train_logs.csv',sep=",",header=T)
norm2<-read.table('norm_clusReso0.4_2/train_logs.csv',sep=",",header=T)
norm3<-read.table('norm_clusReso0.4_3/train_logs.csv',sep=",",header=T)
norm4<-read.table('norm_clusReso0.4_4/train_logs.csv',sep=",",header=T)
norm5<-read.table('norm_clusReso0.4_5/train_logs.csv',sep=",",header=T)

clusReso1<-read.table('norm_clusReso0.5_1/train_logs.csv',sep=",",header=T)
clusReso2<-read.table('norm_clusReso0.5_2/train_logs.csv',sep=",",header=T)
clusReso3<-read.table('norm_clusReso0.5_3/train_logs.csv',sep=",",header=T)
clusReso4<-read.table('norm_clusReso0.5_4/train_logs.csv',sep=",",header=T)
clusReso5<-read.table('norm_clusReso0.5_5/train_logs.csv',sep=",",header=T)

clusResol1<-read.table('norm_clusReso0.6_1/train_logs.csv',sep=",",header=T)
clusResol2<-read.table('norm_clusReso0.6_2/train_logs.csv',sep=",",header=T)
clusResol3<-read.table('norm_clusReso0.6_3/train_logs.csv',sep=",",header=T)
clusResol4<-read.table('norm_clusReso0.6_4/train_logs.csv',sep=",",header=T)
clusResol5<-read.table('norm_clusReso0.6_5/train_logs.csv',sep=",",header=T)

clusResolu1<-read.table('norm_clusReso0.7_1/train_logs.csv',sep=",",header=T)
clusResolu2<-read.table('norm_clusReso0.7_2/train_logs.csv',sep=",",header=T)
clusResolu3<-read.table('norm_clusReso0.7_3/train_logs.csv',sep=",",header=T)
clusResolu4<-read.table('norm_clusReso0.7_4/train_logs.csv',sep=",",header=T)
clusResolu5<-read.table('norm_clusReso0.7_5/train_logs.csv',sep=",",header=T)



####
######

ntop1<-read.table('norm_HVG500/train_logs.csv',sep=",",header=T)
ntop2<-read.table('norm_HVG1000/train_logs.csv',sep=",",header=T)
norm1
ntop3<-read.table('norm_HVG4000/train_logs.csv',sep=",",header=T)
ntop4<-read.table('norm_HVG6000/train_logs.csv',sep=",",header=T)


r<-rbind(r1,r2,r3,r4,r5)
r$type<-'resolution_0.1'
re<-rbind(re1,re2,re3,re4,re5)
re$type<-'resolution_0.2'
res<-rbind(res1,res2,res3,res4,res5)
res$type<-'resolution_0.3'
reso<-rbind(reso1,reso2,reso3,reso4,reso5)
reso$type<-'resolution_0.5'
resol<-rbind(resol1,resol2,resol3,resol4,resol5)
resol$type<-'resolution_0.6'
resolu<-rbind(resolu1,resolu2,resolu3,resolu4,resolu5)
resolu$type<-'resolution_0.7'
resolut<-rbind(resolut1,resolut2,resolut3,resolut4,resolut5)
resolut$type<-'resolution_0.8'
resoluti<-rbind(resoluti1,resoluti2,resoluti3,resoluti4,resoluti5)
resoluti$type<-'resolution_0.9'

n_oo_loop<-rbind(oo1,oo2,oo3,oo4,oo5)
n_oo_loop$type<-'n_oo_loop'
n_oo_loop_n_vv_loop<-rbind(ov1,ov2,ov3,ov4,ov5)
n_oo_loop_n_vv_loop$type<-'n_oo_loop_n_vv_loop'
n_oo_n_oo_loop<-rbind(n1,n2,n3,n4,n5)
n_oo_n_oo_loop$type<-'n_oo_n_oo_loop'
n_oo<-rbind(no1,no2,no3,no4,no5)
n_oo$type<-'n_oo'
n_vv_loop<-rbind(nv1,nv2,nv3,nv4,nv5)
n_vv_loop$type<-'n_vv_loop'

norm<-rbind(norm1,norm2,norm3,norm4,norm5)
norm$type<-'resolution_0.4'

ggplot(d, aes(x = epoch, y = train_loss,fill=type)) +
  geom_point(aes(color = factor(type)), size = 3) +
  geom_smooth(method = "loess", se = FALSE, color = "black")+
  facet_grid(type ~ .) +
  labs(
    x = "epoch",
    y = "test_acc") +
  theme_minimal()

d<-rbind(norm,n_oo_n_oo_loop,n_oo_loop,n_oo_loop_n_vv_loop,n_oo,n_vv_loop)

d<-rbind(norm,r,re,res,reso,resol,resolu)
last_epoch <- subset(d, epoch == 49)
pl2<-ggplot(d, aes(y = test_acc,fill=type)) + 
  geom_boxplot() +
  labs(title = "Boxplot of Test Accuracy", y = "Accuracy")



ggplot(d, aes(x = epoch, y = train_loss,fill=type)) +
  geom_point(aes(color = factor(type)), size = 0.5) +
  geom_smooth(method = "loess", se = FALSE, color = "black")+
  #facet_grid(type ~ ., cols=2) +
  facet_wrap( ~ type, ncol = 3)+
  labs(
       x = "epoch",
       y = "loss_func") +
  theme_minimal()


ntop1$NTOP<-500
ntop2$NTOP<-1000
ntop3$NTOP<-4000
ntop4$NTOP<-6000
norm1$NTOP<-2000
ntops<-rbind(ntop1,ntop2,norm1,ntop3,ntop4)

n_tops_last_epoch <- subset(ntops, epoch == 49)

pl3<-ggplot(ntops, aes(y = test_acc,group= NTOP,fill=NTOP)) + 
  geom_boxplot() +
  labs(title = "Boxplot of Test Accuracy", y = "Accuracy")

ggplot(n_tops_last_epoch, aes(y =test_acc,x= NTOP)) + 
  geom_point(size=4) +
  labs(title = "Boxplot of Test Accuracy", y = "Accuracy")

ggplot(ntops, aes(x = NTOP, y = test_acc)) +
  geom_point(aes( size = 0.5)) +
  geom_smooth(method = "loess", se = FALSE, color = "black")+
  #facet_grid(type ~ ., cols=2) +
 # facet_wrap( ~ type, ncol = 3)+
  labs(
    x = "epoch",
    y = "loss_func") +
  theme_minimal()
