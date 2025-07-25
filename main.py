import asyncio
import time
import json
import aiohttp
from telethon.sync import TelegramClient
from telethon import functions
from telethon.tl.types import InputInvoiceStarGiftResale, InputPeerUser
from config import config


async def send_discord_notification(webhook_url, gift_info, profit_percentage, profit_stars, total_spent, total_bought):
    if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        return
    
    try:
        embed = {
            "title": "🎯 Gift Sniped Successfully!",
            "color": 0x00ff00,
            "fields": [
                {
                    "name": "🎁 Gift Type",
                    "value": gift_info.get('gift_type', 'Unknown'),
                    "inline": True
                },
                {
                    "name": "💰 Purchase Price",
                    "value": f"{gift_info.get('price', 0)} ⭐",
                    "inline": True
                },
                {
                    "name": "📈 Profit Potential",
                    "value": f"{profit_percentage:.1f}% ({profit_stars} ⭐)",
                    "inline": True
                },
                {
                    "name": "🆔 Gift ID",
                    "value": str(gift_info.get('gift_id', 'Unknown')),
                    "inline": True
                },
                {
                    "name": "📊 Session Stats",
                    "value": f"{total_bought} bought • {total_spent} ⭐ spent",
                    "inline": True
                },
                {
                    "name": "⏰ Time",
                    "value": time.strftime('%H:%M:%S'),
                    "inline": True
                }
            ],
            "footer": {
                "text": "TG Star Gift Sniper"
            },
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
        }
        
        payload = {
            "embeds": [embed]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status == 204:
                    print(f"  📨 Discord notification sent successfully")
                else:
                    print(f"  ❌ Discord notification failed: {response.status}")
                    
    except Exception as e:
        print(f"  ❌ Discord notification error: {e}")


async def send_discord_summary(webhook_url, scan_count, total_resale, opportunities_found, scan_duration):
    if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        return
    
    try:
        embed = {
            "title": "📊 Market Scan Summary",
            "color": 0x0099ff,
            "fields": [
                {
                    "name": "🔍 Scan #",
                    "value": str(scan_count),
                    "inline": True
                },
                {
                    "name": "📦 Total Resale Gifts",
                    "value": str(total_resale),
                    "inline": True
                },
                {
                    "name": "💎 Profitable Opportunities",
                    "value": str(opportunities_found),
                    "inline": True
                },
                {
                    "name": "⏱️ Scan Duration",
                    "value": f"{scan_duration:.1f}s",
                    "inline": True
                },
                {
                    "name": "⏰ Time",
                    "value": time.strftime('%H:%M:%S'),
                    "inline": True
                }
            ],
            "footer": {
                "text": "Market Scanner"
            }
        }
        
        payload = {
            "embeds": [embed]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status != 204:
                    print(f"  ❌ Discord summary failed: {response.status}")
                    
    except Exception as e:
        print(f"  ❌ Discord summary error: {e}")


async def get_all_star_gifts(client):
    try:
        result = await client(functions.payments.GetStarGiftsRequest(hash=0))
        return result.gifts if hasattr(result, 'gifts') else []
    except Exception as e:
        print(f"Error fetching star gifts: {e}")
        return []


async def get_resale_gifts_for_gift_id(client, gift_id, gift_index=None, total_gifts=None, min_price=None):
    try:
        result = await client(functions.payments.GetResaleStarGiftsRequest(
            gift_id=gift_id,
            offset="",
            limit=100
        ))
        
        resale_gifts = result.gifts if hasattr(result, 'gifts') else []
        
        if min_price and resale_gifts:
            filtered_for_floor = [gift for gift in resale_gifts if not (120 <= gift.resell_stars <= 140)]
            
            if filtered_for_floor:
                floor_price = min(gift.resell_stars for gift in filtered_for_floor)
                if floor_price < min_price:
                    return []
        
        return resale_gifts
    except Exception as e:
        return []


def calculate_profit_margin(gifts_of_same_type):
    if len(gifts_of_same_type) < 2:
        return 0, 0, None, None
    
    sorted_gifts = sorted(gifts_of_same_type, key=lambda x: x.resell_stars)
    
    lowest_price = sorted_gifts[0].resell_stars
    second_lowest_price = sorted_gifts[1].resell_stars
    
    profit_stars = second_lowest_price - lowest_price
    profit_percentage = (profit_stars / lowest_price) * 100 if lowest_price > 0 else 0
    
    return profit_percentage, profit_stars, sorted_gifts[0], sorted_gifts[1]


def group_gifts_by_type(all_resale_gifts):
    gifts_by_type = {}
    
    for gift in all_resale_gifts:
        gift_key = getattr(gift, 'title', 'Unknown')
        
        if gift_key not in gifts_by_type:
            gifts_by_type[gift_key] = []
        
        gifts_by_type[gift_key].append(gift)
    
    return gifts_by_type


async def scan_all_resale_gifts_concurrent(client, all_gifts, batch_size=50, min_price=None):
    all_resale_gifts = []
    skipped_collections = 0
    
    print(f"🔍 Scanning {len(all_gifts)} gifts for resale listings (concurrent batches of {batch_size})...")
    if min_price:
        print(f"🚫 Skipping collections with floor price < {min_price} stars")
    
    for batch_start in range(0, len(all_gifts), batch_size):
        batch_end = min(batch_start + batch_size, len(all_gifts))
        batch_gifts = all_gifts[batch_start:batch_end]
        
        print(f"  🚀 Processing batch {batch_start//batch_size + 1}/{(len(all_gifts) + batch_size - 1)//batch_size} ({len(batch_gifts)} gifts)...")
        
        tasks = []
        for i, gift in enumerate(batch_gifts):
            task = get_resale_gifts_for_gift_id(
                client, 
                gift.id, 
                batch_start + i, 
                len(all_gifts),
                min_price
            )
            tasks.append(task)
        
        try:
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            batch_gifts_with_resale = 0
            for result in batch_results:
                if isinstance(result, list):
                    if result:
                        all_resale_gifts.extend(result)
                        batch_gifts_with_resale += 1
                elif isinstance(result, Exception):
                    pass
            
            skipped_in_batch = len(batch_gifts) - batch_gifts_with_resale
            skipped_collections += skipped_in_batch
            
            print(f"  ✅ Batch completed: {batch_gifts_with_resale} gifts had qualifying resale items, {skipped_in_batch} skipped")
            
        except Exception as e:
            print(f"  ❌ Batch error: {e}")
        
        if batch_end < len(all_gifts):
            await asyncio.sleep(0.1)
    
    print(f"✅ Concurrent scan complete: Found {len(all_resale_gifts)} qualifying resale gifts")
    print(f"🚫 Skipped {skipped_collections} collections (floor price too low or no resale)")
    return all_resale_gifts


async def scan_all_resale_gifts_sequential(client, all_gifts, min_price=None):
    all_resale_gifts = []
    skipped_collections = 0
    
    print(f"🔍 Scanning {len(all_gifts)} gifts for resale listings (sequential fallback)...")
    if min_price:
        print(f"🚫 Skipping collections with floor price < {min_price} stars")
    
    for i, gift in enumerate(all_gifts):
        try:
            gift_id = gift.id
            resale_gifts = await get_resale_gifts_for_gift_id(client, gift_id, i, len(all_gifts), min_price)
            
            if resale_gifts:
                all_resale_gifts.extend(resale_gifts)
            else:
                skipped_collections += 1
            
            if i % 10 == 0 and i > 0:
                await asyncio.sleep(0.1)
                
        except Exception as e:
            print(f"  ❌ Error checking gift {gift_id}: {e}")
            skipped_collections += 1
            continue
    
    print(f"✅ Sequential scan complete: Found {len(all_resale_gifts)} qualifying resale gifts")
    print(f"🚫 Skipped {skipped_collections} collections (floor price too low or no resale)")
    return all_resale_gifts


async def snipe_gifts_in_range_with_profit(client, gifts, min_price=140, max_price=170, min_profit_percentage=10, webhook_url=None):
    price_filtered_gifts = [gift for gift in gifts if min_price <= gift.resell_stars <= max_price]
    
    if not price_filtered_gifts:
        return 0, 0, []
    
    gifts_by_type = group_gifts_by_type(price_filtered_gifts)
    
    profitable_opportunities = []
    
    print(f"💰 Analyzing profit margins for {len(gifts_by_type)} gift types...")
    
    for gift_type, type_gifts in gifts_by_type.items():
        profit_percentage, profit_stars, lowest_gift, second_lowest_gift = calculate_profit_margin(type_gifts)
        
        if profit_percentage >= min_profit_percentage and lowest_gift:
            profitable_opportunities.append({
                'gift': lowest_gift,
                'profit_percentage': profit_percentage,
                'profit_stars': profit_stars,
                'lowest_price': lowest_gift.resell_stars,
                'second_price': second_lowest_gift.resell_stars if second_lowest_gift else None,
                'gift_type': gift_type
            })
            
            print(f"  💎 {gift_type}: {lowest_gift.resell_stars}→{second_lowest_gift.resell_stars if second_lowest_gift else 'N/A'} stars ({profit_percentage:.1f}% profit)")
    
    if not profitable_opportunities:
        print(f"📉 No gifts meet minimum profit margin of {min_profit_percentage}%")
        return 0, 0, []
    
    profitable_opportunities.sort(key=lambda x: (-x['profit_percentage'], x['lowest_price']))
    
    print(f"🎯 Found {len(profitable_opportunities)} profitable opportunities!")
    
    bought_count = 0
    total_spent = 0
    
    for opportunity in profitable_opportunities:
        gift = opportunity['gift']
        profit_percentage = opportunity['profit_percentage']
        profit_stars = opportunity['profit_stars']
        
        try:
            print(f"🎯 SNIPING: {gift.resell_stars} stars | Profit: {profit_percentage:.1f}% ({profit_stars} ⭐) | Type: {opportunity['gift_type']}")
            
            me = await client.get_me()
            
            invoice = InputInvoiceStarGiftResale(
                slug=gift.slug,  
                to_id=InputPeerUser(user_id=me.id, access_hash=me.access_hash),  
            )
            
            payment_form = await client(functions.payments.GetPaymentFormRequest(
                invoice=invoice
            ))
            
            payment_result = await client(functions.payments.SendStarsFormRequest(
                form_id=payment_form.form_id,
                invoice=invoice
            ))
            
            if payment_result:
                bought_count += 1
                total_spent += gift.resell_stars
                
                print(f"✅ SNIPED! Bought for {gift.resell_stars} stars (potential profit: {profit_percentage:.1f}% / {profit_stars} ⭐)")
                
                gift_info = {
                    'gift_type': opportunity['gift_type'],
                    'price': gift.resell_stars,
                    'gift_id': gift.id,
                }
                
                await send_discord_notification(webhook_url, gift_info, profit_percentage, profit_stars, total_spent, bought_count)
                
            else:
                print(f"❌ Purchase failed - no result")
                
        except Exception as e:
            error_msg = str(e)
            if "GIFT_NOT_AVAILABLE" in error_msg or "ALREADY_SOLD" in error_msg:
                print(f"⚡ Too slow - gift already sold")
            elif "INSUFFICIENT_FUNDS" in error_msg:
                print(f"💸 Insufficient stars balance")
            else:
                print(f"❌ Purchase error: {error_msg}")
    
    return bought_count, total_spent, profitable_opportunities


async def continuous_sniper(client, min_price, max_price, min_profit_percentage, use_concurrent, batch_size, webhook_url):
    print(f"🚀 Starting continuous gift sniper with profit analysis")
    print(f"💰 Target range: {min_price}-{max_price} stars")
    print(f"📈 Minimum profit margin: {min_profit_percentage}%")
    print(f"🚫 Floor price filter: Skip collections < {min_price} stars")
    print(f"⚡ Concurrent scanning: {'ON' if use_concurrent else 'OFF'}")
    if use_concurrent:
        print(f"📦 Batch size: {batch_size}")
    if webhook_url and webhook_url != "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print(f"📨 Discord notifications: ENABLED")
    else:
        print(f"📨 Discord notifications: DISABLED (configure DISCORD_WEBHOOK_URL)")
    print(f"⏱️  Checking every {config.SCAN_INTERVAL} second(s)")
    print("-" * 60)
    
    print("📋 Fetching all available star gifts...")
    all_gifts = await get_all_star_gifts(client)
    
    if not all_gifts:
        print("❌ No star gifts found. Exiting.")
        return
    
    print(f"📦 Found {len(all_gifts)} total star gifts")
    
    with open('all_gifts.json', 'w') as f:
        gift_data = []
        for gift in all_gifts:
            gift_info = {
                'id': gift.id,
                'title': getattr(gift, 'title', 'Unknown'),
                'stars': getattr(gift, 'stars', 0)
            }
            gift_data.append(gift_info)
        json.dump(gift_data, f, indent=2)
    print("💾 Saved gift info to all_gifts.json")
    
    total_bought = 0
    total_spent = 0
    scan_count = 0
    
    while True:
        try:
            scan_start = time.time()
            scan_count += 1
            
            print(f"\n🔄 Scan #{scan_count} - {time.strftime('%H:%M:%S')}")
            
            if use_concurrent:
                all_resale_gifts = await scan_all_resale_gifts_concurrent(client, all_gifts, batch_size, min_price)
            else:
                all_resale_gifts = await scan_all_resale_gifts_sequential(client, all_gifts, min_price)
            
            if all_resale_gifts:
                bought, spent, opportunities = await snipe_gifts_in_range_with_profit(
                    client, all_resale_gifts, min_price, max_price, min_profit_percentage, webhook_url
                )
                
                print(f"📊 Found {len(all_resale_gifts)} qualifying resale gifts, {len(opportunities)} profitable opportunities")
                
                if scan_count % config.SUMMARY_INTERVAL == 0:
                    await send_discord_summary(webhook_url, scan_count, len(all_resale_gifts), len(opportunities), time.time() - scan_start)
                
                if bought > 0:
                    total_bought += bought
                    total_spent += spent
                    print(f"🎉 Session stats: {total_bought} bought, {total_spent} stars spent")
                elif opportunities:
                    print(f"⏳ Found opportunities but couldn't complete purchases")
                else:
                    print(f"📉 No profitable opportunities found")
            else:
                print(f"📭 No qualifying resale gifts found")
            
            scan_duration = time.time() - scan_start
            print(f"⏱️  Scan completed in {scan_duration:.2f}s")
            
            sleep_time = max(0, config.SCAN_INTERVAL - scan_duration)
            
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            else:
                print(f"⚠️  Scan took longer than {config.SCAN_INTERVAL}s interval")
                
        except KeyboardInterrupt:
            print(f"\n🛑 Stopping sniper...")
            print(f"📈 Final stats: {total_bought} gifts bought, {total_spent} stars spent")
            break
        except Exception as e:
            print(f"💥 Error in monitoring loop: {e}")
            await asyncio.sleep(config.SCAN_INTERVAL)


async def main():
    async with TelegramClient(config.SESSION_NAME, config.API_ID, config.API_HASH) as client:
        await continuous_sniper(
            client, 
            config.MIN_PRICE, 
            config.MAX_PRICE, 
            config.MIN_PROFIT_PERCENTAGE, 
            config.USE_CONCURRENT, 
            config.BATCH_SIZE, 
            config.DISCORD_WEBHOOK_URL
        )


if __name__ == "__main__":
    asyncio.run(main())