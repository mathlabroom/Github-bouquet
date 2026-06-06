## Installation command 安装命令  
mkdir -p /tmp/gb_final && wget -qO- https://github.com/mathlabroom/githubbouquet/archive/refs/heads/main.tar.gz | tar -xzf - -C /tmp/gb_final --strip-components=1 && mkdir -p /usr/lib/enigma2/python/Plugins/Extensions/GitHubBouquet && cp -r /tmp/gb_final/ipk_build/usr/lib/enigma2/python/Plugins/Extensions/GitHubBouquet/* /usr/lib/enigma2/python/Plugins/Extensions/GitHubBouquet/ && wget -qO- https://raw.githubusercontent.com/mathlabroom/githubbouquet/main/ipk_build/CONTROL/postinst | sed 's/\r$//' > /tmp/gb_postinst && chmod 755 /tmp/gb_postinst && /tmp/gb_postinst && rm -rf /tmp/gb_final /tmp/gb_postinst && echo "✨ 恭喜老哥，mathlabroom 插件在线直装彻底成功！"

## Enigma2 GitHub Bouquet Custom Update Tool /  Enigma2 GitHub 花束自选更新工具  
增量下载  可自选   Incremental download  Selectable
<img width="859" height="603" alt="image" src="https://github.com/user-attachments/assets/b87fda06-5e59-4e7c-ba82-a150b27d171c" />
<img width="857" height="607" alt="image" src="https://github.com/user-attachments/assets/b9552e23-279d-401e-89e0-8d48d1ab1b32" />
<img width="857" height="605" alt="image" src="https://github.com/user-attachments/assets/f975b451-65de-4f03-aa03-aa5aed12390f" />
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/9a89d1e6-17ff-4d8a-bd69-7a3b58f9f01d" />
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/2dabacd7-aa02-4430-b505-94d048829998" />


