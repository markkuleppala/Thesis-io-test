import json
import math
import numpy as np
import matplotlib.pyplot as plt

def average_runs(volume, rtc, bs, job, rw):
    if 'read' in rw:
        rw_type = 'read'
    else:
        rw_type = 'write'

    bw, iops, N, clat_mean, clat_stddev, clat_50, clat_9999, clat_max = 0, 0, 0, 0, 0, 0, 0, 0
    #clat_percentile = {}
    clat_ms = [0]*4000
    clat_ms_avg = np.zeros(shape=(3,4000))

    results = {}

    for i in range (1, 4):
        with open('{}-{}-{}-{}-{}-{}.json'.format(volume, rtc, bs, job, rw, i)) as f:
            #print('{}-{}-{}-{}-{}-{}.json'.format(volume, rtc, bs, job, rw, i))
            data = json.load(f)
            data = data['jobs'][0][rw_type]

            bw += data['bw']/3
            iops += data['iops']/3

            clat_ns = data['clat_ns']
            N += clat_ns['N']/3
            clat_mean += clat_ns['mean']/3
            clat_stddev += clat_ns['stddev']/3
            clat_50 += clat_ns['percentile']["50.000000"]/3
            clat_9999 += clat_ns['percentile']["99.990000"]/3
            clat_max += clat_ns['max']/3

            for ms in range(1, 4000):
                clat_ms[ms] = clat_ms[ms-1]
                for bin in clat_ns['bins']:
                    if (int(int(bin)/1000) == ms):
                        clat_ms[ms] += clat_ns['bins'][bin]
                    elif (int(int(bin)/1000) > ms):
                        break
            clat_ms_avg[i-1] = clat_ms
    clat_ms_avg = np.mean(clat_ms_avg, axis=0).astype(int)
    

    results['bw'] = int(bw)
    results['iops'] = int(iops)
    results['N'] = int(N)
    results['clat_mean'] = int(clat_mean)
    results['clat_stddev'] = int(clat_stddev)
    results['clat_50'] = int(clat_50)
    results['clat_9999'] = int(clat_9999)
    results['clat_max'] = int(clat_max)
    results['clat_ms_avg'] = clat_ms_avg
    
    return results

def plot_clat_bs(volume, rtc, job, rw):
    legend_loc = 'lower right'
    ms =  np.arange(0, 4000, 1)
    #title = 'Volume: {} RTC: {} Jobs: {} IO-pattern: {}'.format(volume, rtc, job, rw)
    title = '{}'.format(rw)
    for p in range(3): # 3 / 8
        bs = 512*2**p
        results = average_runs(volume, rtc, bs, job, rw)
        label = '{}, 50% {}ms'.format(bs, int(results['clat_50']/1000))
        plt.plot(ms, results['clat_ms_avg']/results['N'], label=label)
    plt.grid(axis='both')
    plt.xscale('log')
    plt.axis([1, 4000, -0.1, 1.1])
    plt.title(title)#, fontsize=12)
    plt.xlabel('Commit latency (ms)')#, fontsize=8)
    plt.ylabel('Cumulative frequency')#, fontsize=8)
    if (results['clat_50']/1000 > 750):
        legend_loc = 'upper left'
    plt.legend(loc=legend_loc, prop={'size': 6})
    #plt.show()

def plot_clat_rw(volume, rtc, bs, job):
    ms = np.arange(0, 4000, 1)
    title = 'Volume: {} RTC: {} Jobs: {} IO-pattern: {}'.format(volume, rtc, job, rw)
    for rw in ['read', 'write', 'randread', 'randwrite']:
        results = average_runs(volume, rtc, job, bs, rw)
        label = '{}, 50% {}ms'.format(bs, int(results['clat_50']/1000))
        plt.plot(ms, results['clat_ms_avg']/results['N'], label=label)
    plt.grid(axis='both')
    plt.xscale('log')
    plt.axis([1, 4000, -0.05, 1.05])
    plt.title(title)
    plt.xlabel('Commit latency (ms)')
    plt.ylabel('Cumulative frequency')
    plt.legend(loc='lower right')
    #plt.show()

def subplot_clat_bs_by_rw(volume, rtc, job):
    for rw in ['read', 'write', 'randread', 'randwrite']:
        if rw == 'read':
            plt.subplot(221)
            #plt.subplots_adjust(wspace=0.5, hspace=0.5)
           # plot_clat_bs(volume, rtc, job, rw)
        elif rw == 'write':
            plt.subplot(222)
            #plt.subplots_adjust(wspace=0.1, hspace=0.2)
            #plot_clat_bs(volume, rtc, job, rw)
        elif rw == 'randread':
            plt.subplot(223)
            #plot_clat_bs(volume, rtc, job, rw)
        elif rw == 'randwrite':
            plt.subplot(224)
            #plot_clat_bs(volume, rtc, job, rw)
        plot_clat_bs(volume, rtc, job, rw)
        plt.subplots_adjust(wspace=0.3, hspace=0.3)
    plt.suptitle('Runtime: {}'.format(rtc))

def plot_clat_bw(volume, job, bs, rw):
    ms =  np.arange(0, 4000, 1)
    #title = 'Volume: {} RTC: {} Jobs: {} IO-pattern: {}'.format(volume, rtc, job, rw)
    title = '{}'.format(rw)
    for rtc in ['bare', 'runc', 'clh', 'qemu', 'qemu-virtiofs']:
        results = average_runs(volume, rtc, job, bs, rw)
        label = '{}, 50% {}ms'.format(rtc, int(results['clat_50']/1000))
        plt.plot(ms, results['clat_ms_avg']/results['N'], label=label)
    plt.grid(axis='both')
    plt.xscale('log')
    plt.axis([1, 4000, -0.1, 1.1])
    plt.title(title)#, fontsize=12)
    plt.xlabel('Commit latency (ms)')#, fontsize=8)
    plt.ylabel('Cumulative frequency')#, fontsize=8)
    plt.legend(loc='lower right', prop={'size': 6})

def subplot_clat_bw_by_rw(volume, job, bs):
    for rw in ['read', 'write', 'randread', 'randwrite']:
        if rw == 'read':
            plt.subplot(221)
        elif rw == 'write':
            plt.subplot(222)
        elif rw == 'randread':
            plt.subplot(223)
        elif rw == 'randwrite':
            plt.subplot(224)
        plot_clat_bw(volume, job, bs, rw)

def main():
    #plot_clat_bs('emptydir-disk', 'clh', 1, 'randread')
    #plot_clat_bs('emptydir-disk', 'clh', 512, 1)
    #subplot_clat_bs_by_rw('emptydir-disk', 'clh', 1)
    #plt.subplots_adjust(wspace=0.3, hspace=0.3)
    #plt.show()
    #subplot_clat_bw_by_rw('emptydir-disk', 1, 1024)
    #subplot_clat_bs_by_rw('bare', 'bare', 1)
    plt.subplots_adjust(wspace=0.3, hspace=0.3)
    plt.show()

if __name__ == "__main__":
    main()
