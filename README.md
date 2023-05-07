### Image
`https://pkgbuild.com/~tpowa/archboot/web/archboot.html`

### Commands
```bash
# Create a new partition table
fdisk /dev/vda # 512M efi (uefi), 512M boot (swap), rest Linux
mkfs.ext4 rest
mkfs.fat -F32 efi
mkswap boot
swapon boot

# mount
mount rest /mnt
mount efi /mnt/boot --mkdir
pacstrap /mnt base base-devel linux linux-firmware archlinuxarm-keyring
genfstab -U /mnt >> /mnt/etc/fstab
arch-chroot /mnt
```