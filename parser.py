import json
import os.path
import numpy as np
import matplotlib.pyplot as plt

def average_runs(volume, rtc, bs, job, rw):
    if 'read' in rw:
        rw_type = 'read'
    else:
        rw_type = 'write'

    ms_max = 30000
    jobs_max = 3
    bw, iops, N, clat_mean, clat_stddev, clat_50, clat_99, clat_9999, clat_max = 0, 0, 0, 0, 0, 0, 0, 0, 0
    clat_ms = [0]*ms_max
    clat_ms_avg = np.zeros(shape=(jobs_max,ms_max))

    results = {}

    for i in range (1, 4):
        with open('{}-{}-{}-{}-{}-{}.json'.format(volume, rtc, bs, job, rw, i)) as f:
            data = json.load(f)
            data = data['jobs'][0][rw_type]

            bw += data['bw']/jobs_max
            iops += data['iops']/jobs_max

            clat_ns = data['clat_ns']
            N += clat_ns['N']/jobs_max
            clat_mean += clat_ns['mean']/jobs_max
            clat_stddev += clat_ns['stddev']/jobs_max
            clat_50 += clat_ns['percentile']["50.000000"]/jobs_max
            clat_99 += clat_ns['percentile']["99.000000"]/jobs_max
            clat_9999 += clat_ns['percentile']["99.990000"]/jobs_max
            clat_max += clat_ns['max']/jobs_max

            for ms in range(1, ms_max):
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
    results['clat_99'] = int(clat_99)
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
    #print(data)
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
    bs_list = [512, 2048, 4096, 8192, 32768, 65536]
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
    #print(data)
    width = 0.10
    if rw == 'read':
        plt.hlines(560, -0.5, len(bs_list)-0.5, colors='c', linestyles='dotted', label='Theoretical max', zorder=0)
    elif rw == 'write':
        plt.hlines(510, -0.5, len(bs_list)-0.5, colors='c', linestyles='dotted', label='Theoretical max', zorder=0)
    plt.bar(X - 2*width, data[0], color = 'b', width = width, label='bare', zorder=1)
    plt.bar(X - width ,  data[1], color = 'g', width = width, label='runc', zorder=1)
    plt.bar(X         ,  data[2], color = 'black', width = width, label='clh', zorder=1)
    plt.bar(X + width ,  data[3], color = 'y', width = width, label='qemu', zorder=1)
    plt.bar(X + 2*width, data[4], color = 'r', width = width, label='qemu-vfs', zorder=1)

    plt.grid(axis='y')
    plt.title(title)#, fontsize=12)
    plt.xlabel('Block size (bytes)')#, fontsize=8)
    plt.ylabel('Bandwidth (MB/s)')#, fontsize=8)
    plt.xticks(X, ['512', '2k', '4k', '8k', '32k', '64k'])

    legend_loc = 'upper left'
    plt.legend(loc=legend_loc, prop={'size': 6})

def plot_bw_by_volume_with_bare(bs, job, rw):
    legend_loc = 'upper left'
    title = '{}'.format(rw)
    rtc_list = ['bare', 'runc', 'clh', 'qemu', 'qemu-virtiofs']
    volume_list = ['emptydir-memory', 'emptydir-disk', 'hostpath', 'pv']
    data = np.empty((len(rtc_list),len(volume_list)))
    X = np.arange(len(volume_list))
    for j in range(len(rtc_list)):
        rtc = rtc_list[j]
        for i in range(len(volume_list)):
            volume = volume_list[i]
            if (rtc == 'bare'):
                results = average_runs('bare', 'bare', bs, job, rw)
            else:
                results = average_runs(volume, rtc, bs, job, rw)
            if (volume == 'emptydir-memory') and (rtc == 'bare'):
                data[j][i] = 0
            else:
                data[j][i] = results['bw']/1000
    #print(data)
    width = 0.10
    if volume != 'emptydir-disk':
        plt.bar(X - 2*width, data[0], color = 'b', width = width, label='bare-metal', zorder=1)
        plt.bar(X - width ,  data[1], color = 'g', width = width, label='runc', zorder=1)
        plt.bar(X         ,  data[2], color = 'black', width = width, label='clh', zorder=1)
        plt.bar(X + width ,  data[3], color = 'y', width = width, label='qemu', zorder=1)
        plt.bar(X + 2*width, data[4], color = 'r', width = width, label='qemu-vfs', zorder=1)
    else:
        plt.bar(X - 3/2*width ,  data[1], color = 'g', width = width, label='runc', zorder=1)
        plt.bar(X - 1/2*width,  data[2], color = 'black', width = width, label='clh', zorder=1)
        plt.bar(X + 1/2*width ,  data[3], color = 'y', width = width, label='qemu', zorder=1)
        plt.bar(X + 3/2*width, data[4], color = 'r', width = width, label='qemu-vfs', zorder=1)

    plt.grid(axis='y')
    plt.title(title)#, fontsize=12)
    plt.xlabel('Volume')#, fontsize=8)
    plt.ylabel('Bandwidth (MB/s)')#, fontsize=8)
    plt.xticks(X, ['ED mem', 'ED disk', 'HP', 'PV'])

    legend_loc = 'upper right'
    plt.legend(loc=legend_loc, prop={'size': 6})

def plot_clat_bs(volume, rtc, job, rw):
    legend_loc = 'lower right'
    ms =  np.arange(0, 30000, 1)
    title = '{}'.format(rw)
    bs_list = ['512', '2048', '4096', '8192', '32768', '65536']
    bs_label = ['512', '2k', '4k', '8k', '32k', '64k']
    for i in range(len(bs_list)):
        results = average_runs(volume, rtc, bs_list[i], job, rw)
        label = '{}, {}ms, {}ms'.format(bs_label[i], int(results['clat_50']/1000), int(results['clat_99']/1000))
        if len(bs_label[i]) == 2:
            label = '{},  {}ms, {}ms'.format(bs_label[i], int(results['clat_50']/1000), int(results['clat_99']/1000))
        plt.plot(ms, results['clat_ms_avg']/results['N'], label=label)
    plt.grid(axis='both')
    plt.xscale('log')
    plt.axis([1, 4000, -0.1, 1.1])
    plt.title(title)#, fontsize=12)
    plt.xlabel('Completion latency (ms)')#, fontsize=8)
    plt.ylabel('Cumulative frequency')#, fontsize=8)
    if (results['clat_50']/1000 > 300):
        legend_loc = 'upper left'
    if (results['clat_99']/1000 > 4000):
        plt.axis([1, 14000, -0.1, 1.1])
    elif (results['clat_99']/1000 > 6000):
        plt.axis([1, 30000, -0.1, 1.1])
    plt.legend(loc=legend_loc, prop={'size': 6}, title='BS, 50th, 99th')

def plot_clat_rw(volume, rtc, bs, job):
    ms = np.arange(0, 30000, 1)
    title = 'Volume: {} RTC: {} Jobs: {}'.format(volume, rtc, job)
    for rw in ['read', 'write', 'randread', 'randwrite']:
        results = average_runs(volume, rtc, job, bs, rw)
        label = '{}, {}ms, {}ms'.format(bs, int(results['clat_50']/1000), int(results['clat_99']/1000))
        plt.plot(ms, results['clat_ms_avg']/results['N'], label=label)
    plt.grid(axis='both')
    plt.xscale('log')
    plt.axis([1, 4000, -0.05, 1.05])
    plt.title(title)
    plt.xlabel('Completion latency (ms)')
    plt.ylabel('Cumulative frequency')
    plt.legend(loc='lower right', title='BS, 50th, 99th')

def plot_clat_bw(volume, job, bs, rw):
    ms =  np.arange(0, 30000, 1)
    title = '{}'.format(rw)
    legend_loc = 'lower right'
    for rtc in ['bare', 'runc', 'clh', 'qemu', 'qemu-virtiofs']:
        if ((rtc == 'bare') and (volume == 'emptydir-memory')):
            continue
        if rtc == 'bare':
            results = average_runs('bare', rtc, bs, job, rw)
        else:
         results = average_runs(volume, rtc, bs, job, rw)
        if (rtc == 'qemu-virtiofs'):
            label = '{}, {}ms, {}ms'.format('qemu-vfs', int(results['clat_50']/1000), int(results['clat_99']/1000))
        else:
            label = '{}, {}ms, {}ms'.format(rtc, int(results['clat_50']/1000), int(results['clat_99']/1000))
        plt.plot(ms, results['clat_ms_avg']/results['N'], label=label)
        
        if (results['clat_50']/1000 > 300):
            legend_loc = 'upper left'
        elif (results['clat_99']/1000 > 1000):
            legend_loc = 'upper left'
    plt.grid(axis='both')
    plt.xscale('log')
    plt.axis([1, 5000, -0.1, 1.1])
    plt.title(title)
    plt.xlabel('Completion latency (ms)')
    plt.ylabel('Cumulative frequency')

    if (results['clat_99']/1000 > 4000):
        plt.axis([1, 14000, -0.1, 1.1])
    elif (results['clat_99']/1000 > 6000):
        plt.axis([1, 30000, -0.1, 1.1])
    plt.legend(loc=legend_loc, prop={'size': 6}, title='RTC, 50th, 99th')

def subplot_clat_bs_by_rw(volume, rtc, job):
    for rw in ['read', 'write', 'randread', 'randwrite']:
        if rw == 'read':
            plt.subplot(221)
        elif rw == 'write':
            plt.subplot(222)
        elif rw == 'randread':
            plt.subplot(223)
        elif rw == 'randwrite':
            plt.subplot(224)
        plot_clat_bs(volume, rtc, job, rw)
        plt.subplots_adjust(wspace=0.3, hspace=0.3)
    if (rtc == 'bare'):
        plt.suptitle('Volume: {}, RTC: {}, Job(s): {}'.format('bare-metal', 'disk', job))
    else:
        plt.suptitle('Volume: {}, RTC: {}, Job(s): {}'.format(volume, rtc, job))

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
        plt.suptitle('Volume: {}, Block size: {}, Job(s): {}'.format(volume, bs, job))

def subplot_bw_by_bs(volume, job):
    for rw in ['read', 'write', 'randread', 'randwrite']:
        if rw == 'read':
            plt.subplot(221)
        elif rw == 'write':
            plt.subplot(222)
        elif rw == 'randread':
            plt.subplot(223)
        elif rw == 'randwrite':
            plt.subplot(224)
        plot_bw(volume, job, rw)
        plt.subplots_adjust(wspace=0.3, hspace=0.3)
    plt.suptitle('Volume: {}, Job(s): {}'.format(volume, job))

def subplot_bw_by_bs_with_bare(volume, job):
    for rw in ['read', 'write', 'randread', 'randwrite']:
        if rw == 'read':
            plt.subplot(221)
        elif rw == 'write':
            plt.subplot(222)
        elif rw == 'randread':
            plt.subplot(223)
        elif rw == 'randwrite':
            plt.subplot(224)
        plot_bw_with_bare(volume, job, rw)
        plt.subplots_adjust(wspace=0.3, hspace=0.3)
    plt.suptitle('Volume: {}, Job(s): {}'.format(volume, job))

def subplot_bw_by_volume_with_bare(bs, job):
    for rw in ['read', 'write', 'randread', 'randwrite']:
        if rw == 'read':
            plt.subplot(221)
        elif rw == 'write':
            plt.subplot(222)
        elif rw == 'randread':
            plt.subplot(223)
        elif rw == 'randwrite':
            plt.subplot(224)
        plot_bw_by_volume_with_bare(bs, job, rw)
        plt.subplots_adjust(wspace=0.3, hspace=0.3)
    plt.suptitle('Block size: {}, Job(s): {}'.format(bs, job))

def main():
    
    #subplot_clat_bs_by_rw_bare
    for job in [1, 2, 3]:
        volume, rtc = 'bare', 'bare'
        if not os.path.isfile('subplot_clat_bs_by_rw({}, {}, {}).pdf'.format(volume, rtc, job)):
            print('subplot_clat_bs_by_rw({}, {}, {}).pdf'.format(volume, rtc, job))
            plt.figure(figsize=[8.0, 8.0])
            subplot_clat_bs_by_rw(volume, rtc, job)
            plt.subplots_adjust(wspace=0.3, hspace=0.3)
            plt.tight_layout()
            plt.savefig('subplot_clat_bs_by_rw({}, {}, {}).pdf'.format('bare', 'bare', job), format='pdf')
            plt.clf()
            plt.close()
    
    #subplot_clat_bs_by_rw
    for volume in ['emptydir-memory', 'emptydir-disk', 'hostpath', 'pv']:
        for rtc in ['runc', 'clh', 'qemu', 'qemu-virtiofs']:
            for job in [1, 2, 3]:
                if not os.path.isfile('subplot_clat_bs_by_rw({}, {}, {}).pdf'.format(volume, rtc, job)):
                    print('subplot_clat_bs_by_rw({}, {}, {}).pdf'.format(volume, rtc, job))
                    plt.figure(figsize=[8.0, 8.0])
                    subplot_clat_bs_by_rw(volume, rtc, job)
                    plt.subplots_adjust(wspace=0.3, hspace=0.3)
                    plt.tight_layout()
                    plt.savefig('subplot_clat_bs_by_rw({}, {}, {}).pdf'.format(volume, rtc, job), format='pdf')
                    plt.clf()
                    plt.close()
    
    #subplot_clat_bw_by_rw
    for bs in [512, 1024, 2048, 4096, 8192, 32768, 65536]:
        for job in [1, 2, 3]:
            for volume in ['emptydir-memory', 'emptydir-disk', 'hostpath', 'pv']:
                if not os.path.isfile('subplot_clat_bw_by_rw({}, {}, {}).pdf'.format(volume, job, bs)):
                    print('subplot_clat_bw_by_rw({}, {}, {}).pdf'.format(volume, job, bs))
                    plt.figure(figsize=[8.0, 8.0])
                    subplot_clat_bw_by_rw(volume, job, bs)
                    plt.subplots_adjust(wspace=0.3, hspace=0.3)
                    plt.tight_layout()
                    plt.savefig('subplot_clat_bw_by_rw({}, {}, {}).pdf'.format(volume, job, bs), format='pdf')
                    plt.clf()
                    plt.close()

    #subplot_bw_by_volume_with_bare
    for bs in [512, 1024, 2048, 4096, 8192, 32768, 65536]:
        for job in [1, 2, 3]:
            if not os.path.isfile('subplot_bw_by_volume_with_bare({}, {}).pdf'.format(bs, job)):
                print('subplot_bw_by_volume_with_bare({}, {}).pdf'.format(bs, job))
                plt.figure(figsize=[8.0, 8.0])
                subplot_bw_by_volume_with_bare(bs, job)
                plt.subplots_adjust(wspace=0.3, hspace=0.3)
                plt.tight_layout()
                plt.savefig('subplot_bw_by_volume_with_bare({}, {}).pdf'.format(bs, job), format='pdf')
                plt.clf()
                plt.close()

    #subplot_bw_by_bs_with_bare
    for volume in ['emptydir-memory', 'emptydir-disk', 'hostpath', 'pv']:
        for job in [1, 2, 3]:
            if not os.path.isfile('subplot_bw_by_bs_with_bare({}, {}).pdf'.format(volume, job)):
                print('subplot_bw_by_bs_with_bare({}, {}).pdf'.format(volume, job))
                plt.figure(figsize=[8.0, 8.0])
                subplot_bw_by_bs_with_bare(volume, job)
                plt.subplots_adjust(wspace=0.3, hspace=0.3)
                plt.tight_layout()
                plt.savefig('subplot_bw_by_bs_with_bare({}, {}).pdf'.format(volume, job), format='pdf')
                plt.clf()
                plt.close()

if __name__ == "__main__":
    main()
