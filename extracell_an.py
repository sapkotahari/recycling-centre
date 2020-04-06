def get_threshold(channel,sdmult=4):
    """gets the threshold as 4*SD"""
    try:
        chan_ar=channel.as_array()
    except:
        chan_ar=channel
    #Is the mean == channel baseline?
    threshold= chan_ar.mean()+(sdmult*chan_ar.std())
    return threshold

def remove_large_spikes(channel, large_spk_mult=7):
    #find positive spikes
    large_pos_spikes_ind=np.where(channel.as_array()>get_threshold(channel,large_spk_mult))[0]
    #find negative spikes
    large_neg_spikes_ind=np.where(channel.as_array()<-get_threshold(channel,large_spk_mult))[0]
    #put them together 
    large_spikes_ind=list(large_pos_spikes_ind)+list(large_neg_spikes_ind)
    #remove them
    channel_no_large_spikes= channel.duplicate_with_new_data(
            np.delete(channel,large_spikes_ind))
    return channel_no_large_spikes

def find_peaks(channel,  event_points=10, positive_only=0,threshold=None):
    """find peaks above a threshold, if positive_only==1 it only thaks positive peaks.
    event_points gives number of points describing the event, 
    high numbers will reduce false positive but increase false negatives """ 
    if threshold==None: threshold=get_threshold(channel)
     
    #gets all the positive first
    supra_thres=np.where((channel.as_array())>get_threshold(channel),channel,0)
    polarity=np.greater
    #find all possible peaks above positive threshold
    event_inds=(sig.argrelextrema(supra_thres,polarity, axis=0, order=(event_points), mode='clip'))
    event_inds=event_inds[0]
     #if you also want the negatives
    if positive_only!=1:#need to change polarity
        print("Both positive and negative events will be analysed")
        neg_supra_thres=np.where((channel.as_array())<-get_threshold(channel),channel,0)
        neg_event_inds=(sig.argrelextrema(neg_supra_thres,np.less, axis=0, order=(event_points), mode='clip'))
        neg_event_inds=neg_event_inds[0]
        event_inds=list(event_inds)+list(neg_event_inds)
    else: print("Only positive events will be analysed")
    print("with a "+str(event_points)+" points time window")
    return list(event_inds)

def plot_spikes(channel,spk_ind=None):
    """plots spikes as red dots on the black trace"""
    if spk_ind==None: find_peaks(channel)
    ch_ar=channel.as_array()
    plt.figure;
    plt.plot(channel.times,channel,'k')
    plt.plot(channel.times[spk_ind],ch_ar[spk_ind],'ro')
 
def coastline(channel):
    """returns the coastline using the formula in Niknazar et al.2013  
    only the array part of the neo analog signals is used"""
    return np.sum(np.absolute(np.diff(channel.as_array()[:,0])))

def find_art(rec):
    """find large events that go above threshold on more than one channel at the time
    and returns their position. This only works with 16Channels array end files 
    exported with  16 channels""" 
    #pick channels to be used
    chs=[rec.analogsignals[0].as_array(),rec.analogsignals[15].as_array()]#for now limited to two channels
    art_threshold=0.8  #intended to be relative to the max value
    
    #take both positive and negative for both channels
    #for channel in chs:
    
    art_inds=list(set(supra_thres[0])&set(supra_thres[1]))
    
    
    return art_inds
