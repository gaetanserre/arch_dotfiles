### Commands
```bash
# Create a new partition table
fdisk /dev/sda # 4G swap (swap), rest Linux
mkfs.ext4 rest
mkswap swap
swapon swap

# mount
mount rest /mnt
mount efi_win /mnt/efi --mkdir
pacstrap -K ara/mnt base base-devel linux linux-firmware
genfstab -U /mnt >> /mnt/etc/fstab
arch-chroot /mnt
```