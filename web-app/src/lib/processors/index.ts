import { BaseProcessor } from './BaseProcessor';
import { MixxProcessor } from './MixxProcessor';
import { AoshiProcessor } from './AoshiProcessor';
import { C2CProcessor } from './C2CProcessor';
import { ShoplineProcessor } from './ShoplineProcessor';
import { Platform } from '../types/order';

export { BaseProcessor, MixxProcessor, AoshiProcessor, C2CProcessor, ShoplineProcessor };

export function createProcessor(platform: Platform): BaseProcessor {
  switch (platform) {
    case 'mixx':
      return new MixxProcessor();
    case 'aoshi':
      return new AoshiProcessor();
    case 'c2c':
      return new C2CProcessor();
    case 'shopline':
      return new ShoplineProcessor();
    default:
      throw new Error(`Unsupported platform: ${platform}`);
  }
}
