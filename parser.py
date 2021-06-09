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
        print('{}-{}-{}-{}-{}-{}.json'.format(volume, rtc, bs, job, rw, i))
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

def plot_bw(volume, job, rw):
    legend_loc = 'upper left'
    ms =  np.arange(0, 4000, 1)
    #title = 'Volume: {} RTC: {} Jobs: {} IO-pattern: {}'.format(volume, rtc, job, rw)
    title = '{}'.format(rw)
    rtc_list = ['runc', 'clh', 'qemu', 'qemu-virtiofs']
    bs_list = [512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
    data = np.empty((len(rtc_list),len(bs_list)))
    X = np.arange(len(bs_list))
    for j in range(len(rtc_list)):
        rtc = rtc_list[j]
        for i in range(len(bs_list)):
            bs = bs_list[i]
            results = average_runs(volume, rtc, bs, job, rw)
            data[j][i] = results['bw']/1000
    print(data)
    width = 0.10
    plt.bar(X - 1.5*width, data[0], color = 'b', width = width, label='runc')
    plt.bar(X - width/2, data[1], color = 'g', width = width, label='clh')
    plt.bar(X + width/2, data[2], color = 'y', width = width, label='qemu')
    plt.bar(X + 1.5*width, data[3], color = 'r', width = width, label='qemu-vfs')
    plt.grid(axis='y')
    plt.title(title)#, fontsize=12)
    plt.xlabel('Block size (bytes)')#, fontsize=8)
    plt.ylabel('Bandwidth (MB/s)')#, fontsize=8)
    plt.xticks(X, ['512', '1k', '2k', '4k', '8k', '16k', '32k', '64k'])

    legend_loc = 'upper left'
    plt.legend(loc=legend_loc, prop={'size': 6})

def plot_bw_with_bare(volume, job, rw):
    legend_loc = 'upper left'
    ms =  np.arange(0, 4000, 1)
    title = '{}'.format(rw)
    rtc_list = ['bare', 'runc', 'clh', 'qemu', 'qemu-virtiofs']
    bs_list = [512, 2048, 8192, 32768, 65536]
    data = np.empty((len(rtc_list),len(bs_list)))
    X = np.arange(len(bs_list))
    for j in range(len(rtc_list)):
        rtc = rtc_list[j]
        for i in range(len(bs_list)):
            bs = bs_list[i]
            if (rtc == 'bare'):
                results = average_runs('bare', rtc, bs, job, rw)
            else:
                results = average_runs(volume, rtc, bs, job, rw)
            data[j][i] = results['bw']/1000
    print(data)
    width = 0.10
    if rw == 'read':
        plt.hlines(560, -0.5, 3.5, colors='c', linestyles='dotted', label='Theoretical max')
    elif rw == 'write':
        plt.hlines(510, -0.5, 3.5, colors='c', linestyles='dotted', label='Theoretical max')
    plt.bar(X - 2*width, data[0], color = 'b', width = width, label='bare')
    plt.bar(X - width ,  data[1], color = 'g', width = width, label='runc')
    plt.bar(X         ,  data[2], color = 'black', width = width, label='clh')
    plt.bar(X + width ,  data[3], color = 'y', width = width, label='qemu')
    plt.bar(X + 2*width, data[4], color = 'r', width = width, label='qemu-vfs')

    plt.grid(axis='y')
    plt.title(title)#, fontsize=12)
    plt.xlabel('Block size (bytes)')#, fontsize=8)
    plt.ylabel('Bandwidth (MB/s)')#, fontsize=8)
    plt.xticks(X, ['512', '2k', '4k', '32k', '64k'])

    legend_loc = 'upper left'
    plt.legend(loc=legend_loc, prop={'size': 6})

def plot_clat_bs(volume, rtc, job, rw):
    legend_loc = 'lower right'
    ms =  np.arange(0, 4000, 1)
    #title = 'Volume: {} RTC: {} Jobs: {} IO-pattern: {}'.format(volume, rtc, job, rw)
    title = '{}'.format(rw)
    bs_list = ['512', '2048', '8192', '32768', '65536']
    for bs in bs_list:
    #for p in range(8):
        #bs = 512*2**p
        results = average_runs(volume, rtc, bs, job, rw)
        label = '{}, 50% {}ms'.format(bs, int(results['clat_50']/1000))
        plt.plot(ms, results['clat_ms_avg']/results['N'], label=label)
    plt.grid(axis='both')
    plt.xscale('log')
    plt.axis([1, 4000, -0.1, 1.1])
    plt.title(title)#, fontsize=12)
    plt.xlabel('Completion latency (ms)')#, fontsize=8)
    plt.ylabel('Cumulative frequency')#, fontsize=8)
    if (results['clat_50']/1000 > 750):
        legend_loc = 'upper left'
    plt.legend(loc=legend_loc, prop={'size': 6})

def plot_clat_rw(volume, rtc, bs, job):
    ms = np.arange(0, 4000, 1)
    title = 'Volume: {} RTC: {} Jobs: {}'.format(volume, rtc, job)
    for rw in ['read', 'write', 'randread', 'randwrite']:
        results = average_runs(volume, rtc, job, bs, rw)
        label = '{}, 50% {}ms'.format(bs, int(results['clat_50']/1000))
        plt.plot(ms, results['clat_ms_avg']/results['N'], label=label)
    plt.grid(axis='both')
    plt.xscale('log')
    plt.axis([1, 4000, -0.05, 1.05])
    plt.title(title)
    plt.xlabel('Completion latency (ms)')
    plt.ylabel('Cumulative frequency')
    plt.legend(loc='lower right')
    #plt.show()

def subplot_clat_bs_by_rw(volume, job):
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
        plot_clat_bs(volume, job, rw)
        plt.subplots_adjust(wspace=0.3, hspace=0.3)
    plt.suptitle('Volume: {}'.format(volume))

def subplot_bw_by_bs(volume, job):
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
        plot_bw(volume, job, rw)
        plt.subplots_adjust(wspace=0.3, hspace=0.3)
    plt.suptitle('Volume: {}, Job(s): {}'.format(volume, job))

def subplot_bw_by_bs_with_bare(volume, job):
    for rw in ['randread']:#, 'randwrite']:#['read', 'write', 'randread', 'randwrite']:
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
        plot_bw_with_bare(volume, job, rw)
        plt.subplots_adjust(wspace=0.3, hspace=0.3)
    plt.suptitle('Volume: {}, Job(s): {}'.format(volume, job))

def plot_clat_bw(volume, job, bs, rw):
    ms =  np.arange(0, 4000, 1)
    #title = 'Volume: {} RTC: {} Jobs: {} IO-pattern: {}'.format(volume, rtc, job, rw)
    title = '{}'.format(rw)
    for rtc in ['runc', 'clh', 'qemu', 'qemu-virtiofs']:
        results = average_runs(volume, rtc, job, bs, rw)
        if (rtc == 'qemu-virtiofs'):
            label = '{}, 50% {}ms'.format('qemu-vfs', int(results['clat_50']/1000))
        else:
            label = '{}, 50% {}ms'.format(rtc, int(results['clat_50']/1000))
        plt.plot(ms, results['clat_ms_avg']/results['N'], label=label)
    plt.grid(axis='both')
    plt.xscale('log')
    plt.axis([1, 4000, -0.1, 1.1])
    plt.title(title)#, fontsize=12)
    plt.xlabel('Completion latency (ms)')#, fontsize=8)
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
        plt.suptitle('Block size: {}'.format(bs))

def main():
    #plot_clat_bs('emptydir-disk', 'clh', 1, 'randread')
    #plot_clat_bs('emptydir-disk', 'clh', 512, 1)
    #subplot_clat_bs_by_rw('emptydir-disk', 'clh', 1)
    #plt.subplots_adjust(wspace=0.3, hspace=0.3)
    #plt.show()
    #subplot_clat_bw_by_rw('pv', 1, 1024)
    #subplot_clat_bs_by_rw('hostpath', 'qemu', 1)
    #subplot_bw_by_bs('emptydir-disk', 3)
    subplot_bw_by_bs_with_bare('emptydir-disk', 1)
    plt.subplots_adjust(wspace=0.3, hspace=0.3)
    plt.show()

if __name__ == "__main__":
    main()
