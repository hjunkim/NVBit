#!/usr/bin/python
import sys
import re

PAGE_SHIFT=12
PAGE_SIZE=(1<<PAGE_SHIFT) # 4KB
PAGE_MASK=(~(PAGE_SIZE-1))

WARP_SIZE=32 # warp size: 32

def refactor(conts, file_name):
	epoch = 0
	epoch_i = 0
	kernel_name = ''
	i_kernel = 0
	grids_sum = 1
	blocks_sum = 1
	t_addr_list = list()
	is_first_kernel=True
	
	for line in conts:

		# Kernel info., calculate # warps
		if 'Kernel' and 'shmem' and 'nregs' in line:
			toks = re.split('-', line)
			t_kernel_name = re.split(' ', toks[0])
			kernel_name = re.split('[\\(]', t_kernel_name[1])[0]
			print (kernel_name)
			grids_sum = 1
			blocks_sum = 1

			if is_first_kernel is True:
				is_first_kernel=False
			else:
				fpw.close()
			
			fpw = open(str(i_kernel)+'_'+kernel_name+'_'+file_name, 'w')

			grids = re.split(',', toks[1])
			grids[0]=re.split(' ', grids[0])[3]
			blocks = re.split(',', toks[2])
			blocks[0]=re.split(' ', blocks[0])[3]

			for g in grids:
				grids_sum *= int(g)
			for b in blocks:
				blocks_sum *= int(b)

			epoch = grids_sum * blocks_sum / WARP_SIZE
			i_kernel += 1
		
		# 
		if 'CTA' in line:
			toks = re.split('-', line)
			addr_list=re.split(' ', toks[3])
			page_num=''
			addr_list=list(set(addr_list))
			
			for addr in addr_list:
				if '0x' in addr:
					page_num=int(addr, 16) & PAGE_MASK
					t_str = str(epoch_i/epoch)+','+str(page_num)+'\n'
					if t_str not in t_addr_list:
						fpw.write(t_str)
						t_addr_list.append(t_str)
			epoch_i += 1

	fpw.close()


def main():
	if len(sys.argv) < 2:
		sys.stderr.write('./refactor.py <filename>.trace\n')
		exit()

	file_name = str(sys.argv[1])
	with open(file_name, "r") as fpr:
		contents = fpr.readlines()
		refactor(contents, file_name)

	fpr.close()
	
if __name__ == '__main__':
	main()
